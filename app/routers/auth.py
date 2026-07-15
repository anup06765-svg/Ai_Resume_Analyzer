from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from app.auth.password import hash_password, verify_password

from app.database.database import get_db
from app.models.user import User

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



from app.crud.user_crud import (
    get_user_by_email,
    create_user,
    authenticate_user
)

# ============================
# Register Page
# ============================

@router.get("/register")
def register_page(request: Request):
    templates = request.app.state.templates
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
    templates = request.app.state.templates

    existing_user = get_user_by_email(
    db,
    email
)

    if existing_user:

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email already registered.",
                "success": None
            }
        )

    create_user(
    db=db,
    full_name=full_name,
    email=email,
    password=password
)

    return RedirectResponse(

        url="/auth/login",

        status_code=status.HTTP_303_SEE_OTHER

    )


# ============================
# Login Page
# ============================

@router.get("/login")
def login_page(request: Request):
    templates = request.app.state.templates

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
@limiter.limit("5/minute")
def login_user(

    request: Request,

    email: str = Form(...),

    password: str = Form(...),

    db: Session = Depends(get_db)

):
    templates = request.app.state.templates

    user = authenticate_user(
    db=db,
    email=email,
    password=password
)

    if user is None:

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

