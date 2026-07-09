from sqlalchemy.orm import Session

from app.models.user import User

from app.auth.password import hash_password


# ----------------------------
# Check Existing Email
# ----------------------------

def get_user_by_email(
        db: Session,
        email: str
):

    return db.query(User).filter(
        User.email == email
    ).first()


# ----------------------------
# Create New User
# ----------------------------

def create_user(

        db: Session,

        full_name: str,

        email: str,

        password: str

):

    hashed_password = hash_password(password)

    new_user = User(

        full_name=full_name,

        email=email,

        password=hashed_password

    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# ----------------------------
# Get User By ID
# ----------------------------

def get_user_by_id(

        db: Session,

        user_id: int

):

    return db.query(User).filter(

        User.id == user_id

    ).first()


# ----------------------------
# Get All Users
# ----------------------------

def get_all_users(

        db: Session

):

    return db.query(User).all()