from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Checks if a user is logged in (via session).
    If not logged in, stops the request immediately and redirects to login.
    If logged in, returns the User object.
    """

    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth/login"}
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth/login"}
        )

    return user


def login_required(
    request: Request,
    db: Session = Depends(get_db)
):
    return get_current_user(
        request=request,
        db=db
    )

def hr_required(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Sirf HR role wale users ko HR section me aane deta hai.
    """

    user = get_current_user(request=request, db=db)

    if user.role != "hr":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/dashboard/"}
        )

    return user


def candidate_required(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Agar HR galti se candidate dashboard par aa jaaye to
    use uske apne HR dashboard par bhej do.
    """

    user = get_current_user(request=request, db=db)

    if user.role == "hr":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/hr/dashboard"}
        )

    return user