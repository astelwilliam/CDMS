from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


ALLOWED_USER_ROLES = frozenset({"super_admin", "department_admin"})


class PrivilegedUserMutationDenied(Exception):
    """The actor may not perform the requested authorization-state mutation."""


class UserMutationTargetNotFound(Exception):
    """The requested target user does not exist."""


@dataclass(frozen=True)
class LockedUserMutation:
    actor: User
    target: User


def lock_privileged_user_mutation(
    db: Session,
    actor_user_id: str,
    target_user_id: str,
) -> LockedUserMutation:
    """Lock actor and target users in ID order and revalidate privilege."""
    users = list(
        db.scalars(
            select(User)
            .where(User.id.in_({actor_user_id, target_user_id}))
            .order_by(User.id)
            .with_for_update()
        )
    )
    users_by_id = {user.id: user for user in users}
    actor = users_by_id.get(actor_user_id)
    if actor is None or not actor.is_active or actor.role != "super_admin":
        raise PrivilegedUserMutationDenied

    target = users_by_id.get(target_user_id)
    if target is None:
        raise UserMutationTargetNotFound
    return LockedUserMutation(actor=actor, target=target)


def stage_user_role_change(
    db: Session,
    actor_user_id: str,
    target_user_id: str,
    new_role: str,
) -> User:
    """Stage an exact supported role change without committing or rolling back."""
    if new_role not in ALLOWED_USER_ROLES:
        raise ValueError("Unsupported user role")

    locked = lock_privileged_user_mutation(db, actor_user_id, target_user_id)
    if locked.actor.id == locked.target.id and new_role != "super_admin":
        raise PrivilegedUserMutationDenied

    locked.target.role = new_role
    db.flush()
    return locked.target


def stage_user_activation_change(
    db: Session,
    actor_user_id: str,
    target_user_id: str,
    is_active: bool,
) -> User:
    """Stage an activation change without committing or rolling back."""
    if type(is_active) is not bool:
        raise ValueError("is_active must be a boolean")

    locked = lock_privileged_user_mutation(db, actor_user_id, target_user_id)
    if locked.actor.id == locked.target.id and not is_active:
        raise PrivilegedUserMutationDenied

    locked.target.is_active = is_active
    db.flush()
    return locked.target
