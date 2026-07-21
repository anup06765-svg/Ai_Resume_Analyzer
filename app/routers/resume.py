from fastapi import (
    APIRouter,
    Request,
    Depends,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import RedirectResponse, FileResponse
from starlette import status

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import login_required
from app.models.hr_profile import HRProfile
from app.models.resume import Resume

from app.services.file_services import FileService
from app.services.pdf_parser import PDFParser
from app.services.analysis_service import AnalysisService


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


def get_post_upload_redirect(user) -> str:
    if getattr(user, "role", None) == "hr":
        return "/hr/dashboard"
    return "/dashboard/"


# ===================================================
# Upload Resume Page
# ===================================================

@router.get("/upload")
def upload_page(
    request: Request,
    user=Depends(login_required)
):
    templates = request.app.state.templates

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
    templates = request.app.state.templates

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

            user_id=user.id,

            hr_profile_id=_get_default_hr_profile_id(db, user)

        )

        db.add(new_resume)

        db.commit()

        db.refresh(new_resume)

        # -------------------------
        # Run Analysis
        # -------------------------

        AnalysisService.analyze_resume(new_resume)

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

    return RedirectResponse(
        url=get_post_upload_redirect(user),
        status_code=status.HTTP_303_SEE_OTHER
    )


def _get_default_hr_profile_id(db: Session, user) -> int | None:
    if getattr(user, "role", None) != "hr":
        return None

    profile = (
        db.query(HRProfile)
        .filter(HRProfile.hr_id == user.id)
        .order_by(HRProfile.id.desc())
        .first()
    )

    if profile:
        return profile.id

    # HR ka abhi tak koi Job Profile nahi hai (isliye resume kisi se
    # bhi link nahi ho paata aur HR Dashboard par hamesha 0 dikhta
    # hai). Isse bachne ke liye ek default "General" profile khud
    # bana dete hain, taaki resume kabhi bhi orphan (hr_profile_id
    # = None) na rahe aur dashboard par turant count ho jaaye.

    default_profile = HRProfile(
        title="General",
        hr_id=user.id
    )

    db.add(default_profile)
    db.commit()
    db.refresh(default_profile)

    return default_profile.id


# ===================================================
# View / Download Resume (Secure)
# ===================================================

@router.get("/view/{resume_id}")
def view_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Securely serve a resume PDF.
    Only the owner of the resume can view/download it.
    """

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    file_path = FileService.get_file_path(resume.filepath)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found on server."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=resume.filename
    )


# ===================================================
# Resume History Page
# ===================================================

@router.get("/history")
def resume_history(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Shows a list of all resumes uploaded by the logged-in user.
    """

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .all()
    )

    templates = request.app.state.templates

    return templates.TemplateResponse(
        "resume_history.html",
        {
            "request": request,
            "user": user,
            "resumes": resumes
        }
    )