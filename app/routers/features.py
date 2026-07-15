import json

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import login_required
from app.models.resume import Resume
from app.services.jd_matching_service import jd_matching_service
from app.models.contact import ContactMessage
from fastapi.responses import RedirectResponse,FileResponse
from app.services.email_service import send_contact_email
from app.auth.password import verify_password, hash_password

from slowapi import Limiter
from slowapi.util import get_remote_address

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO
from fastapi.responses import StreamingResponse

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    tags=["Features"]
)


# ===================================================
# ATS Report Page
# ===================================================

@router.get("/ats")
def ats_report(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .first()
    )

    ats_score = 0
    ats_grade = "N/A"
    matched_skills = []
    missing_skills = []
    suggestions = []
    breakdown = {}
    breakdown_items = []

    if latest_resume:

        ats_score = latest_resume.ats_score or 0
        ats_grade = latest_resume.ats_grade or "N/A"

        if latest_resume.analysis_result:

            try:

                analysis = json.loads(latest_resume.analysis_result)

                matched_skills = analysis.get("matched_skills", [])
                missing_skills = analysis.get("missing_skills", [])
                suggestions = analysis.get("suggestions", [])
                breakdown = analysis.get("breakdown", {})

            except Exception:
                pass

    breakdown_config = [
        ("Skills Match", "fa-solid fa-code", "skills", 40),
        ("Resume Length", "fa-solid fa-file-lines", "resume_length", 20),
        ("Education", "fa-solid fa-graduation-cap", "education", 10),
        ("Projects", "fa-solid fa-diagram-project", "projects", 10),
        ("Experience", "fa-solid fa-briefcase", "experience", 10),
        ("Contact Info", "fa-solid fa-address-card", "contact", 10),
    ]

    breakdown_items = []

    for label, icon, key, max_value in breakdown_config:

        value = breakdown.get(key, 0)
        percent = (value / max_value * 100) if max_value else 0

        breakdown_items.append({
            "label": label,
            "icon": icon,
            "value": value,
            "max": max_value,
            "percent": percent
        })

    radius = 90
    circumference = 2 * 3.1416 * radius

    ats_offset = circumference - (
        ats_score / 100
    ) * circumference

    templates = request.app.state.templates

    return templates.TemplateResponse(
        "ats_report.html",
        {
            "request": request,
            "user": user,
            "latest_resume": latest_resume,
            "ats_score": ats_score,
            "ats_grade": ats_grade,
            "ats_offset": ats_offset,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "breakdown_items": breakdown_items
        }
    )


# ===================================================
# Job Matching Page (Show Form)
# ===================================================

@router.get("/job-matching")
def job_matching_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .all()
    )

    templates = request.app.state.templates

    return templates.TemplateResponse(
        "job_matching.html",
        {
            "request": request,
            "user": user,
            "resumes": resumes,
            "result": None,
            "match_offset": None,
            "selected_resume_id": None,
            "jd_text": "",
            "error": None
        }
    )


# ===================================================
# Job Matching (Run Analysis)
# ===================================================

@router.post("/job-matching")
def job_matching_analyze(
    request: Request,
    resume_id: int = Form(...),
    jd_text: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .all()
    )

    templates = request.app.state.templates

    selected_resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user.id
        )
        .first()
    )

    if not selected_resume:

        return templates.TemplateResponse(
            "job_matching.html",
            {
                "request": request,
                "user": user,
                "resumes": resumes,
                "result": None,
                "match_offset": None,
                "selected_resume_id": resume_id,
                "jd_text": jd_text,
                "error": "Selected resume not found."
            }
        )

    if not jd_text or not jd_text.strip():

        return templates.TemplateResponse(
            "job_matching.html",
            {
                "request": request,
                "user": user,
                "resumes": resumes,
                "result": None,
                "match_offset": None,
                "selected_resume_id": resume_id,
                "jd_text": jd_text,
                "error": "Please paste a job description before analyzing."
            }
        )

    resume_skills = []

    if selected_resume.analysis_result:

        try:

            analysis = json.loads(selected_resume.analysis_result)

            resume_skills = analysis.get("analysis", {}).get("skills", [])

        except Exception:
            resume_skills = []

    result = jd_matching_service.analyze(
        resume_skills=resume_skills,
        jd_text=jd_text
    )

    radius = 90
    circumference = 2 * 3.1416 * radius

    match_offset = circumference - (
        result["matching_score"] / 100
    ) * circumference

    return templates.TemplateResponse(
        "job_matching.html",
        {
            "request": request,
            "user": user,
            "resumes": resumes,
            "result": result,
            "match_offset": match_offset,
            "selected_resume_id": resume_id,
            "jd_text": jd_text,
            "error": None
        }
    )

# ===================================================
# AI Suggestions Page
# ===================================================

@router.get("/ai-analysis")
def ai_suggestions_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Shows AI-generated suggestions to improve the user's latest resume.
    """

    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .first()
    )

    suggestions = []
    ats_score = 0
    ats_grade = "N/A"
    detected_skills = []

    if latest_resume:

        ats_score = latest_resume.ats_score or 0
        ats_grade = latest_resume.ats_grade or "N/A"

        if latest_resume.analysis_result:

            try:

                analysis = json.loads(latest_resume.analysis_result)

                suggestions = analysis.get("suggestions", [])
                detected_skills = analysis.get("analysis", {}).get("skills", [])

            except Exception:
                pass

    templates = request.app.state.templates

    return templates.TemplateResponse(
        "ai_suggestions.html",
        {
            "request": request,
            "user": user,
            "latest_resume": latest_resume,
            "suggestions": suggestions,
            "ats_score": ats_score,
            "ats_grade": ats_grade,
            "detected_skills": detected_skills
        }
    )

# ===================================================
# Profile Page
# ===================================================

@router.get("/profile")
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Shows the logged-in user's profile details and resume stats.
    """

    total_resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .count()
    )

    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .first()
    )

    average_ats_score = 0

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .all()
    )

    if resumes:

        scores = [r.ats_score or 0 for r in resumes]
        average_ats_score = round(sum(scores) / len(scores), 1)

    templates = request.app.state.templates

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "total_resumes": total_resumes,
            "latest_resume": latest_resume,
            "average_ats_score": average_ats_score
        }
    )




# ===================================================
# Contact Form Submission
# ===================================================

@router.post("/contact")
@limiter.limit("3/minute")
async def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Saves a contact form submission to the database.
    Does not require login — anyone visiting the site can submit.
    """

    new_message = ContactMessage(
        name=name,
        email=email,
        message=message
    )

    db.add(new_message)
    db.commit()

    # Try sending an email notification (won't crash if it fails)
    send_contact_email(name=name, email=email, message=message)

    return RedirectResponse(
        url="/?contact_success=1#contact-info",
        status_code=303
    )






# ===================================================
# Change Password Page
# ===================================================

@router.get("/change-password")
def change_password_page(
    request: Request,
    user=Depends(login_required)
):
    templates = request.app.state.templates

    return templates.TemplateResponse(
        "change_password.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "success": None
        }
    )


# ===================================================
# Change Password (Submit)
# ===================================================

@router.post("/change-password")
def change_password_submit(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    templates = request.app.state.templates

    # -------------------------
    # Verify current password
    # -------------------------

    if not verify_password(current_password, user.password):

        return templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "user": user,
                "error": "Current password is incorrect.",
                "success": None
            }
        )

    # -------------------------
    # Check new passwords match
    # -------------------------

    if new_password != confirm_password:

        return templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "user": user,
                "error": "New passwords do not match.",
                "success": None
            }
        )

    # -------------------------
    # Check minimum length
    # -------------------------

    if len(new_password) < 6:

        return templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "user": user,
                "error": "New password must be at least 6 characters.",
                "success": None
            }
        )

    # -------------------------
    # Prevent same password reuse
    # -------------------------

    if verify_password(new_password, user.password):

        return templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "user": user,
                "error": "New password must be different from current password.",
                "success": None
            }
        )

    # -------------------------
    # Update password
    # -------------------------

    user.password = hash_password(new_password)

    db.commit()

    return templates.TemplateResponse(
        "change_password.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "success": "Password updated successfully!"
        }
    )


# ===================================================
# Download ATS Report as PDF
# ===================================================

@router.get("/ats/pdf")
def download_ats_report_pdf(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(login_required)
):
    """
    Generates and downloads the ATS report as a PDF file.
    """

    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == user.id)
        .order_by(Resume.id.desc())
        .first()
    )

    if not latest_resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found."
        )

    ats_score = latest_resume.ats_score or 0
    ats_grade = latest_resume.ats_grade or "N/A"
    matched_skills = []
    missing_skills = []
    suggestions = []
    breakdown = {}

    if latest_resume.analysis_result:
        try:
            analysis = json.loads(latest_resume.analysis_result)
            matched_skills = analysis.get("matched_skills", [])
            missing_skills = analysis.get("missing_skills", [])
            suggestions = analysis.get("suggestions", [])
            breakdown = analysis.get("breakdown", {})
        except Exception:
            pass

    # ------------------------------------
    # Generate PDF
    # ------------------------------------

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        alignment=1
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=10,
        spaceBefore=10
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#475569'),
        spaceAfter=6
    )

    # ------------------------------------
    # Build PDF content
    # ------------------------------------

    elements = []

    # Title
    elements.append(Paragraph("ATS Report", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Score section
    elements.append(Paragraph("Overall Score", heading_style))
    score_table_data = [
        ["ATS Score", "Grade"],
        [f"{ats_score}/100", ats_grade]
    ]
    score_table = Table(score_table_data, colWidths=[2.5*inch, 2.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.2*inch))

    # Score breakdown
    elements.append(Paragraph("Score Breakdown", heading_style))
    breakdown_data = [
        ["Category", "Score", "Max"]
    ]
    for label, key, max_val in [
        ("Skills Match", "skills", 40),
        ("Resume Length", "resume_length", 20),
        ("Education", "education", 10),
        ("Projects", "projects", 10),
        ("Experience", "experience", 10),
        ("Contact Info", "contact", 10),
    ]:
        value = breakdown.get(key, 0)
        breakdown_data.append([label, str(value), str(max_val)])

    breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.25*inch, 1.25*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(breakdown_table)
    elements.append(Spacer(1, 0.2*inch))

    # Skills section
    elements.append(Paragraph("Skills Analysis", heading_style))
    elements.append(Paragraph(f"Matched Skills ({len(matched_skills)}): {', '.join(matched_skills) if matched_skills else 'None'}", normal_style))
    elements.append(Paragraph(f"Missing Skills ({len(missing_skills)}): {', '.join(missing_skills) if missing_skills else 'None'}", normal_style))
    elements.append(Spacer(1, 0.2*inch))

    # Suggestions section
    elements.append(Paragraph("Suggestions to Improve", heading_style))
    for suggestion in suggestions:
        elements.append(Paragraph(f"• {suggestion}", normal_style))

    if not suggestions:
        elements.append(Paragraph("No suggestions — your resume looks good!", normal_style))

    # ------------------------------------
    # Build and save PDF
    # ------------------------------------

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ats_report.pdf"}
    )