import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import login_required
from app.models.resume import Resume

from app.services.pdf_parser import PDFParser
from app.services.nlp_service import resume_nlp_service
from app.services.ats_services import ATSService

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post("/run/{resume_id}")
def analyze_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Analyze uploaded resume and save ATS result.
    """

    # -----------------------------------
    # Login Check
    # -----------------------------------

    if hasattr(user, "status_code"):
        return user

    # -----------------------------------
    # Resume Ownership Check
    # -----------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user.id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # -----------------------------------
    # Build Absolute PDF Path
    # -----------------------------------

    pdf_path = Path("app/uploads") / resume.filepath

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found."
        )

    # -----------------------------------
    # Extract Resume Text
    # -----------------------------------

    try:

        resume_text = PDFParser.extract_text(
            str(pdf_path)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF parsing failed: {str(e)}"
        )

    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from PDF."
        )

    # Save parsed text

    resume.parsed_text = resume_text

    # -----------------------------------
    # NLP Analysis
    # -----------------------------------

    extracted_data = (
        resume_nlp_service.analyze_resume(
            resume_text
        )
    )

    # -----------------------------------
    # ATS Score
    # -----------------------------------

    result = ATSService.calculate(resume_text)

    # -----------------------------------
    # Save Analysis
    # -----------------------------------

    resume.ats_score = result["ats_score"]

    resume.ats_grade = result["ats_grade"]

    resume.analysis_result = json.dumps(
    result,
    ensure_ascii=False
)

    db.commit()

    db.refresh(resume)

    # -----------------------------------
    # Response
    # -----------------------------------

    return {

        "success": True,

        "message": "Resume analyzed successfully.",

        "resume_id": resume.id,

        "candidate": extracted_data.get("name"),

        "ats_score": resume.ats_score,

        "grade": resume.ats_grade,

        "breakdown": result["breakdown"],

        "resume_data": extracted_data

    }