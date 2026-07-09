from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.auth.password import hash_password


class UserService:

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()


    @staticmethod
    def create_user(
        db: Session,
        full_name: str,
        email: str,
        password: str
    ):

        # Remove Spaces
        full_name = full_name.strip()
        email = email.strip().lower()

        # Duplicate Email Check
        existing_user = UserService.get_user_by_email(
            db,
            email
        )

        if existing_user:
            return {
                "success": False,
                "message": "Email already registered."
            }

        # Password Hash
        hashed_password = hash_password(password)

        try:

            user = User(
                full_name=full_name,
                email=email,
                password=hashed_password
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return {
                "success": True,
                "message": "Registration Successful",
                "user": user
            }

        except SQLAlchemyError:

            db.rollback()

            return {
                "success": False,
                "message": "Database Error"
            }


    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ):

        return db.query(User).filter(
            User.id == user_id
        ).first()