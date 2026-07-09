from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resume import Resume
from app.dependencies.auth import login_required

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):

    if isinstance(user, RedirectResponse):
        return user

    # ------------------------------------
    # Get User Resumes
    # ------------------------------------

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .all()
    )

    total_resumes = len(resumes)

    latest_resume = resumes[0] if resumes else None

    # ------------------------------------
    # Default Values
    # ------------------------------------

    ats_score = 0
    ats_grade = "N/A"
    matched_skills = 0
    missing_skills = 0
    job_match = 0

    # ------------------------------------
    # Latest Resume Data
    # ------------------------------------

    if latest_resume:

        ats_score = latest_resume.ats_score
        ats_grade = latest_resume.ats_grade

        # Temporary values
        # Next step me analysis_result se calculate karenge

        matched_skills = 12
        missing_skills = 4
        job_match = ats_score

    # ------------------------------------
    # Circular Gauge
    # ------------------------------------

    radius = 90
    circumference = 2 * 3.1416 * radius

    ats_offset = circumference - (
        ats_score / 100
    ) * circumference

    # ------------------------------------
    # Dashboard
    # ------------------------------------

    return request.app.state.templates.TemplateResponse(

        "dashboard.html",

        {

            "request": request,

            "user": user,

            "ats_score": ats_score,

            "ats_grade": ats_grade,

            "ats_offset": ats_offset,

            "total_resumes": total_resumes,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "job_match": job_match,

            "latest_resume": latest_resume

        }

    )