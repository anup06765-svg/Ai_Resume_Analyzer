from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        request.session.clear()

        return RedirectResponse(
            url="/auth/login",
            status_code=302
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