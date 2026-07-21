from sqlalchemy.orm import Session

from app.models.user import User

from app.auth.password import hash_password

from app.auth.password import verify_password

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

        password: str,

        role: str = "candidate"

):

    hashed_password = hash_password(password)

    if role not in ("candidate", "hr"):
        role = "candidate"

    new_user = User(

        full_name=full_name,

        email=email,

        password=hashed_password,

        role=role

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

# ----------------------------
# Authenticate User
# ----------------------------




def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    """
    Authenticate user using email and password.
    Returns User object if credentials are valid.
    Otherwise returns None.
    """

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user