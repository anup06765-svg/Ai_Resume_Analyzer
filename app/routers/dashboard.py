import json

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import login_required
from app.models.resume import Resume

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

    matched_skills = []
    missing_skills = []
    suggestions = []

    word_count = 0
    job_match = 0

    # ------------------------------------
    # Load Analysis Result
    # ------------------------------------

    if latest_resume:

        ats_score = latest_resume.ats_score or 0
        ats_grade = latest_resume.ats_grade or "N/A"

        if latest_resume.analysis_result:

            try:

                analysis = json.loads(
                    latest_resume.analysis_result
                )

                matched_skills = analysis.get(
                    "matched_skills",
                    []
                )

                missing_skills = analysis.get(
                    "missing_skills",
                    []
                )

                suggestions = analysis.get(
                    "suggestions",
                    []
                )

                word_count = analysis.get(
                    "word_count",
                    0
                )

                job_match = ats_score

            except Exception:

                matched_skills = []
                missing_skills = []
                suggestions = []
                word_count = 0
                job_match = ats_score

    # ------------------------------------
    # ATS Gauge
    # ------------------------------------

    radius = 90
    circumference = 2 * 3.1416 * radius

    ats_offset = circumference - (
        ats_score / 100
    ) * circumference

    # ------------------------------------
    # Render Dashboard
    # ------------------------------------

    response = request.app.state.templates.TemplateResponse(

        "dashboard.html",

        {

            "request": request,

            "user": user,

            "total_resumes": total_resumes,

            "latest_resume": latest_resume,

            "ats_score": ats_score,

            "ats_grade": ats_grade,

            "ats_offset": ats_offset,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "suggestions": suggestions,

            "word_count": word_count,

            "job_match": job_match

        }

    )
    
    # Browser ko dashboard page cache/bfcache me store karne se roko
    # (taaki logout ke baad back button se purana dashboard na dikhe)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response