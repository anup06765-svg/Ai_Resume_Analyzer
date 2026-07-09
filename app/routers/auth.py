from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.database.database import get_db
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================
# Register Page
# ============================

@router.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "error": None,
            "success": None
        }
    )


# ============================
# Register User
# ============================

@router.post("/register")
def register_user(

    request: Request,

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    db: Session = Depends(get_db)

):

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email already registered.",
                "success": None
            }
        )

    hashed_password = pwd_context.hash(password)

    user = User(

        full_name=full_name,

        email=email,

        password=hashed_password

    )

    db.add(user)

    db.commit()

    return RedirectResponse(

        url="/auth/login",

        status_code=status.HTTP_303_SEE_OTHER

    )


# ============================
# Login Page
# ============================

@router.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(

        "login.html",

        {
            "request": request,
            "error": None,
            "success": None
        }

    )


# ============================
# Login User
# ============================

@router.post("/login")
def login_user(

    request: Request,

    email: str = Form(...),

    password: str = Form(...),

    db: Session = Depends(get_db)

):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:

        return templates.TemplateResponse(

            "login.html",

            {
                "request": request,
                "error": "Invalid Email or Password",
                "success": None
            }

        )

    if not pwd_context.verify(password, user.password):

        return templates.TemplateResponse(

            "login.html",

            {
                "request": request,
                "error": "Invalid Email or Password",
                "success": None
            }

        )

    request.session["user_id"] = user.id

    request.session["user_name"] = user.full_name

    return RedirectResponse(

        url="/dashboard/",

        status_code=status.HTTP_303_SEE_OTHER

    )


# ============================
# Logout
# ============================

@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    response = RedirectResponse(
        url="/auth/login",
        status_code=302
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

