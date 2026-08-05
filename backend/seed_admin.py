import sys
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository


def seed_super_admin():
    db: Session = SessionLocal()

    try:
        user_repo = UserRepository(db)

        email = "admin@cdms.com"

        # Check if admin already exists
        if user_repo.exists_by_email(email):
            print(f"Super Admin already exists with email: {email}")
            return

        admin_user = User(
            email=email,
            hashed_password=hash_password("Admin@123"),
            role="super_admin",
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Super Admin created successfully!")
        print(f"Email: {email}")
        print("Password: Admin@123")
        print("Role: super_admin")

    except Exception as e:
        db.rollback()
        print(f"Error creating Super Admin: {e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    seed_super_admin()