from fastapi import (
    APIRouter,
    Request,
    Depends,
    UploadFile,
    File
)

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import login_required
from app.models.resume import Resume

from app.services.file_service import FileService
from app.services.pdf_parser import PDFParser


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


# ===================================================
# Upload Resume Page
# ===================================================

@router.get("/upload")
def upload_page(
    request: Request,
    user=Depends(login_required)
):

    if hasattr(user, "status_code"):
        return user

    return templates.TemplateResponse(
        "upload_resume.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "success": None
        }
    )


# ===================================================
# Upload Resume
# ===================================================

@router.post("/upload")
async def upload_resume(
    request: Request,
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(login_required)
):

    # -------------------------
    # Session Check
    # -------------------------

    if hasattr(user, "status_code"):
        return user

    # -------------------------
    # Validate PDF
    # -------------------------

    valid, error = await FileService.validate_pdf(resume)

    if not valid:

        return templates.TemplateResponse(
            "upload_resume.html",
            {
                "request": request,
                "user": user,
                "error": error,
                "success": None
            }
        )

    # -------------------------
    # Save PDF
    # -------------------------

    success, filename, error = await FileService.save_pdf(resume)

    if not success:

        return templates.TemplateResponse(
            "upload_resume.html",
            {
                "request": request,
                "user": user,
                "error": error,
                "success": None
            }
        )

    # -------------------------
    # Extract Resume Text
    # -------------------------

    try:

        parsed_text = PDFParser.extract_text(
            f"app/uploads/{filename}"
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        FileService.delete_file(filename)

        return templates.TemplateResponse(
            "upload_resume.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "success": None
            }
        )

    # -------------------------
    # Save Database
    # -------------------------

    try:

        new_resume = Resume(

            filename=resume.filename,

            filepath=filename,

            parsed_text=parsed_text,

            user_id=user.id

        )

        db.add(new_resume)

        db.commit()

        db.refresh(new_resume)

    except Exception as e:

        import traceback

        traceback.print_exc()

        db.rollback()

        FileService.delete_file(filename)

        return templates.TemplateResponse(
            "upload_resume.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "success": None
            }
        )

    # -------------------------
    # Success
    # -------------------------

    return templates.TemplateResponse(
        "upload_resume.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "success": "Resume uploaded and parsed successfully."
        }
    )