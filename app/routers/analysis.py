from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.models.resume import Resume

from app.services.pdf_parser import PDFParser
from app.services.nlp_service import resume_nlp_service
from app.services.ats_services import ATSScorer
router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post("/run/{resume_id}")
def analyze_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):

    # -----------------------------------
    # Find Resume
    # -----------------------------------

    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:

        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # -----------------------------------
    # Extract PDF Text
    # -----------------------------------

    resume_text = PDFParser.extract_text(
    resume.filepath
    )

    if not resume_text:

        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from PDF."
        )

    # Save parsed text

    resume.parsed_text = resume_text

    # -----------------------------------
    # NLP Analysis
    # -----------------------------------

    extracted_data = resume_nlp_service.analyze_resume(
    resume_text
    )

    # -----------------------------------
    # ATS Score
    # -----------------------------------

    ats = ATSScorer()

    result = ats.calculate_score(
        extracted_data
    )

    # -----------------------------------
    # Save Analysis
    # -----------------------------------

    resume.ats_score = result["ats_score"]

    resume.ats_grade = result["grade"]

    resume.analysis_result = json.dumps(
        extracted_data,
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