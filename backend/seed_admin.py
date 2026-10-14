import getpass
import sys

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.administrator_provisioning import (
    AdministratorAlreadyProvisioned,
    AdministratorEmailUnavailable,
    InvalidAdministratorCredentials,
    has_super_administrator,
    stage_initial_super_administrator,
)


def provision_super_admin(
    session_factory=SessionLocal,
    input_fn=input,
    password_fn=getpass.getpass,
) -> int:
    """Interactively provision the first super-admin login identity."""
    db: Session = session_factory()

    try:
        if has_super_administrator(db):
            print("A super administrator is already provisioned.")
            return 0

        email = input_fn("Super administrator email: ").strip()
        password = password_fn("Password: ")
        confirmation = password_fn("Confirm password: ")
        if password != confirmation:
            print("Provisioning failed: passwords do not match.", file=sys.stderr)
            return 1

        stage_initial_super_administrator(db, email, password)
        db.commit()
        print("Super administrator provisioned successfully.")
        return 0
    except AdministratorAlreadyProvisioned:
        db.rollback()
        print("A super administrator is already provisioned.")
        return 0
    except (AdministratorEmailUnavailable, InvalidAdministratorCredentials):
        db.rollback()
        print("Provisioning failed: invalid or unavailable credentials.", file=sys.stderr)
        return 1
    except Exception:
        db.rollback()
        print("Provisioning failed.", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(provision_super_admin())
