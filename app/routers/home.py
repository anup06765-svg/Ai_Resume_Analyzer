from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    contact_success = request.query_params.get("contact_success")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "contact_success": contact_success
        }
    )


@router.get("/upload-resume")
async def upload_resume_redirect(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/resume/upload",
            status_code=302
        )

    return RedirectResponse(
        url="/auth/register",
        status_code=302
    )

