from unittest.mock import MagicMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.privileged_user_mutation import (
    PrivilegedUserMutationDenied,
    UserMutationTargetNotFound,
    lock_privileged_user_mutation,
    stage_user_activation_change,
    stage_user_role_change,
)


def users():
    actor = User(
        id="actor-user",
        email="actor@example.com",
        hashed_password="unused",
        role="super_admin",
        is_active=True,
    )
    target = User(
        id="target-user",
        email="target@example.com",
        hashed_password="unused",
        role="department_admin",
        is_active=True,
    )
    return actor, target


def session_returning(*rows):
    db = MagicMock(spec=Session)
    db.scalars.return_value = rows
    return db


def test_privileged_lock_orders_users_and_uses_for_update():
    actor, target = users()
    db = session_returning(actor, target)

    locked = lock_privileged_user_mutation(db, actor.id, target.id)

    assert locked.actor is actor
    assert locked.target is target
    statement = db.scalars.call_args.args[0]
    sql = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
    assert "ORDER BY users.id" in sql
    assert sql.endswith("FOR UPDATE")


def test_role_change_flushes_without_commit_or_rollback():
    actor, target = users()
    db = session_returning(actor, target)

    assert stage_user_role_change(
        db, actor.id, target.id, "super_admin"
    ) is target
    assert target.role == "super_admin"
    db.flush.assert_called_once_with()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_activation_change_flushes_without_commit_or_rollback():
    actor, target = users()
    db = session_returning(actor, target)

    assert stage_user_activation_change(
        db, actor.id, target.id, False
    ) is target
    assert target.is_active is False
    db.flush.assert_called_once_with()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


@pytest.mark.parametrize(
    "actor_changes",
    [{"role": "department_admin"}, {"is_active": False}],
)
def test_current_database_actor_state_must_be_active_super_admin(actor_changes):
    actor, target = users()
    for field, value in actor_changes.items():
        setattr(actor, field, value)
    db = session_returning(actor, target)

    with pytest.raises(PrivilegedUserMutationDenied):
        stage_user_activation_change(db, actor.id, target.id, False)

    assert target.is_active is True
    db.flush.assert_not_called()


def test_missing_target_fails_closed():
    actor, target = users()
    db = session_returning(actor)

    with pytest.raises(UserMutationTargetNotFound):
        stage_user_role_change(db, actor.id, target.id, "super_admin")
    db.flush.assert_not_called()


@pytest.mark.parametrize(
    "operation",
    [
        lambda db, user_id: stage_user_role_change(
            db, user_id, user_id, "department_admin"
        ),
        lambda db, user_id: stage_user_activation_change(
            db, user_id, user_id, False
        ),
    ],
)
def test_actor_cannot_remove_own_super_admin_access(operation):
    actor, _ = users()
    db = session_returning(actor)

    with pytest.raises(PrivilegedUserMutationDenied):
        operation(db, actor.id)
    db.flush.assert_not_called()


@pytest.mark.parametrize("new_role", ["unknown", "SUPER_ADMIN", ""])
def test_unsupported_roles_are_rejected_before_locking(new_role):
    db = MagicMock(spec=Session)
    with pytest.raises(ValueError, match="Unsupported user role"):
        stage_user_role_change(db, "actor", "target", new_role)
    db.scalars.assert_not_called()
    db.flush.assert_not_called()


@pytest.mark.parametrize("field,value", [("role", "super_admin"), ("is_active", False)])
def test_generic_user_repository_cannot_change_authorization_fields(field, value):
    actor, target = users()
    db = MagicMock(spec=Session)
    repo = UserRepository(db)

    with pytest.raises(ValueError, match="privileged user mutation service"):
        repo.update(target, {field: value})

    db.commit.assert_not_called()
    assert target.role == "department_admin"
    assert target.is_active is True
