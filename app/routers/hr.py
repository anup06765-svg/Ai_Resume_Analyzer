import json
from typing import List, Optional

from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import RedirectResponse
from starlette import status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import hr_required
from app.models.hr_profile import HRProfile
from app.models.resume import Resume

from app.services.file_services import FileService
from app.services.pdf_parser import PDFParser
from app.services.analysis_service import AnalysisService
from app.services.hr_service import HRService
from app.services.jd_matching_service import jd_matching_service


router = APIRouter(
    prefix="/hr",
    tags=["HR"]
)


# ===================================================
# HR Dashboard - sirf HR ka apna data
# ===================================================

@router.get("/dashboard")
def hr_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    profiles = (
        db.query(HRProfile)
        .filter(HRProfile.hr_id == user.id)
        .order_by(HRProfile.id.desc())
        .all()
    )

    profile_cards = []

    total_candidates = 0
    total_shortlisted = 0
    scores_sum = 0
    scores_count = 0

    for profile in profiles:

        total = len(profile.resumes)

        shortlisted = sum(
            1 for r in profile.resumes if r.is_shortlisted
        )

        best_score = max(
            (r.combined_score or r.ats_score or 0 for r in profile.resumes),
            default=0
        )

        has_jd = bool(profile.job_description and profile.job_description.strip())

        profile_cards.append({
            "profile": profile,
            "total": total,
            "shortlisted": shortlisted,
            "best_score": best_score,
            "has_jd": has_jd
        })

        total_candidates += total
        total_shortlisted += shortlisted

        for r in profile.resumes:
            scores_sum += (r.combined_score or r.ats_score or 0)
            scores_count += 1

    avg_score = round(scores_sum / scores_count) if scores_count else 0

    response = request.app.state.templates.TemplateResponse(
        "hr_dashboard.html",
        {
            "request": request,
            "user": user,
            "profile_cards": profile_cards,
            "total_profiles": len(profiles),
            "total_candidates": total_candidates,
            "total_shortlisted": total_shortlisted,
            "avg_score": avg_score
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ===================================================
# Create a new Job Profile
# ===================================================

@router.get("/profile/create")
def create_profile_page(
    request: Request,
    user=Depends(hr_required)
):
    return request.app.state.templates.TemplateResponse(
        "hr_profile_create.html",
        {
            "request": request,
            "user": user,
            "error": None
        }
    )


@router.post("/profile/create")
def create_profile(
    request: Request,
    title: str = Form(...),
    job_description: str = Form(""),
    shortlist_threshold: int = Form(70),
    ats_weight: int = Form(50),
    jd_weight: int = Form(50),
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    templates = request.app.state.templates

    if not title.strip():
        return templates.TemplateResponse(
            "hr_profile_create.html",
            {
                "request": request,
                "user": user,
                "error": "Profile title is required."
            }
        )

    # HR khud fill karta hai — bas basic sanity check (0-100 range)
    shortlist_threshold, ats_weight, jd_weight = _sanitize_scoring_settings(
        shortlist_threshold, ats_weight, jd_weight, current=None
    )

    profile = HRProfile(
        title=title.strip(),
        job_description=job_description.strip() or None,
        hr_id=user.id,
        shortlist_threshold=shortlist_threshold,
        ats_weight=ats_weight,
        jd_weight=jd_weight
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return RedirectResponse(
        url=f"/hr/profile/{profile.id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


# ===================================================
# Delete an entire Job Profile (aur uske sabhi resumes)
# ===================================================

@router.post("/profile/{profile_id}/delete")
def delete_job_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    # Pehle confirm karo ye profile isi HR ki hai
    profile = _get_owned_profile(db, profile_id, user.id)

    # Profile ke andar ke sabhi resumes ki PDF files disk se hataao
    for resume in profile.resumes:
        FileService.delete_file(resume.filepath)

    # Profile delete karne se uske sabhi resumes bhi (cascade se)
    # automatically DB se delete ho jaayenge
    db.delete(profile)
    db.commit()

    return RedirectResponse(
        url="/hr/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )


# ===================================================
# Profile detail: candidates ranked top -> bottom,
# shortlisted highlighted
# ===================================================

@router.get("/profile/{profile_id}")
def profile_detail(
    profile_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    profile = _get_owned_profile(db, profile_id, user.id)

    resumes = (
        db.query(Resume)
        .filter(Resume.hr_profile_id == profile.id)
        .order_by(Resume.combined_score.desc())
        .all()
    )

    remaining_for_shortlist = 0

    response = request.app.state.templates.TemplateResponse(
        "hr_profile_detail.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "resumes": resumes,
            "total": len(resumes),
            "remaining_for_shortlist": remaining_for_shortlist,
            "jd_required_skills": _extract_jd_skills(profile.job_description),
            "error": None,
            "success": None
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ===================================================
# HR khud is profile ke shortlisting settings fill/update
# karta hai (threshold + ATS/JD weightage)
# ===================================================

@router.post("/profile/{profile_id}/settings")
def update_profile_settings(
    profile_id: int,
    shortlist_threshold: Optional[int] = Form(None),
    ats_weight: Optional[int] = Form(None),
    jd_weight: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    profile = _get_owned_profile(db, profile_id, user.id)

    # current=profile: agar koi field missing/invalid aaye, to
    # profile ki ABHI ki saved value hi bani rahegi — kabhi bhi
    # chup-chaap kisi hardcoded default (jaise 50) pe reset nahi
    # hoga
    shortlist_threshold, ats_weight, jd_weight = _sanitize_scoring_settings(
        shortlist_threshold, ats_weight, jd_weight, current=profile
    )

    profile.shortlist_threshold = shortlist_threshold
    profile.ats_weight = ats_weight
    profile.jd_weight = jd_weight
    db.commit()
    db.refresh(profile)

    # Naye weightage ke hisaab se sabhi existing resumes ka
    # combined_score dobara nikalo
    resumes = (
        db.query(Resume)
        .filter(Resume.hr_profile_id == profile.id)
        .all()
    )

    for resume in resumes:
        analysis_output = AnalysisService.analyze_resume(resume)
        extracted_skills = analysis_output["analysis"].get("skills", [])
        _apply_jd_matching(resume, profile, extracted_skills)

    db.commit()

    # Naye threshold ke hisaab se shortlist status refresh karo
    HRService.recalculate_shortlist(db, profile.id)

    return RedirectResponse(
        url=f"/hr/profile/{profile.id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


# ===================================================
# Bulk upload resumes into a profile (10, 20, 50 ek saath)
# ===================================================

@router.post("/profile/{profile_id}/upload")
async def bulk_upload_resumes(
    profile_id: int,
    request: Request,
    resumes: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    profile = _get_owned_profile(db, profile_id, user.id)
    templates = request.app.state.templates

    saved_count = 0
    failed_files = []

    for resume_file in resumes:

        valid, error = await FileService.validate_pdf(resume_file)

        if not valid:
            failed_files.append(f"{resume_file.filename}: {error}")
            continue

        success, filename, error = await FileService.save_pdf(resume_file)

        if not success:
            failed_files.append(f"{resume_file.filename}: {error}")
            continue

        try:
            parsed_text = PDFParser.extract_text(f"app/uploads/{filename}")

            new_resume = Resume(
                filename=resume_file.filename,
                filepath=filename,
                parsed_text=parsed_text,
                user_id=user.id,
                hr_profile_id=profile.id,
                candidate_name=_guess_candidate_name(resume_file.filename)
            )

            db.add(new_resume)
            db.commit()
            db.refresh(new_resume)

            analysis_output = AnalysisService.analyze_resume(new_resume)
            extracted_skills = analysis_output["analysis"].get("skills", [])

            _apply_jd_matching(new_resume, profile, extracted_skills)

            db.commit()

            saved_count += 1

        except Exception as e:
            db.rollback()
            FileService.delete_file(filename)
            failed_files.append(f"{resume_file.filename}: {str(e)}")

    HRService.recalculate_shortlist(db, profile.id)

    # Profile ko dobara fresh DB se le lo — is se guarantee hota hai
    # ki shortlist_threshold / ats_weight / jd_weight (jo HR ne save
    # kiya tha) resume-upload ke baad bhi bilkul wahi dikhega, kisi
    # bhi tarah se reset/change nahi hoga
    db.refresh(profile)

    all_resumes = (
        db.query(Resume)
        .filter(Resume.hr_profile_id == profile.id)
        .order_by(Resume.combined_score.desc())
        .all()
    )

    remaining_for_shortlist = 0

    success_msg = f"{saved_count} resume(s) uploaded & analyzed."
    if failed_files:
        success_msg += f" {len(failed_files)} file(s) skipped."

    return templates.TemplateResponse(
        "hr_profile_detail.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "resumes": all_resumes,
            "total": len(all_resumes),
            "remaining_for_shortlist": remaining_for_shortlist,
            "jd_required_skills": _extract_jd_skills(profile.job_description),
            "error": "; ".join(failed_files) if failed_files else None,
            "success": success_msg
        }
    )


# ===================================================
# Helpers
# ===================================================

def _get_owned_profile(db: Session, profile_id: int, hr_id: int) -> HRProfile:
    profile = (
        db.query(HRProfile)
        .filter(
            HRProfile.id == profile_id,
            HRProfile.hr_id == hr_id
        )
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return profile


def _guess_candidate_name(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    name = name.replace("_", " ").replace("-", " ").strip()
    return name.title() if name else "Candidate"


def _extract_jd_skills(job_description: str) -> list:
    """
    Profile ki Job Description se required skills nikalta hai
    (candidate side wale hi jd_matching_service se, dashboard par
    dikhane ke liye).
    """

    if not job_description or not job_description.strip():
        return []

    return jd_matching_service.extract_jd_skills(job_description)


def _sanitize_scoring_settings(
    shortlist_threshold,
    ats_weight,
    jd_weight,
    current: HRProfile = None
):
    """
    HR jo bhi values khud fill kare, unhe EXACTLY wahi save/dikhaya
    jaata hai — bas ek 0-100 range check hota hai taaki galat input
    se scoring na toote. Pehle ye function dono weights ko zabardasti
    100 tak "normalize" kar deta tha (isi wajah se HR ke diye values
    badal ke kabhi-kabhi 50/50 show ho jaate the) — ab aisa NAHI hota.
    Agar koi value missing/invalid ho, to (naya profile banate waqt)
    ek sensible default use hota hai, ya (existing profile edit karte
    waqt) us profile ki ABHI ki saved value hi wapas rakh di jaati hai
    — kabhi bhi chup-chaap 50/50 pe reset nahi hota.
    """

    def _clamp(value, fallback):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return fallback
        return max(0, min(100, value))

    fallback_threshold = current.shortlist_threshold if current else 70
    fallback_ats = current.ats_weight if current else 50
    fallback_jd = current.jd_weight if current else 50

    shortlist_threshold = _clamp(shortlist_threshold, fallback_threshold)
    ats_weight = _clamp(ats_weight, fallback_ats)
    jd_weight = _clamp(jd_weight, fallback_jd)

    return shortlist_threshold, ats_weight, jd_weight


def _apply_jd_matching(resume: Resume, profile: HRProfile, resume_skills: list):
    """
    Candidate section ka JD-matching engine (jd_matching_service) HR
    ke bulk-upload ke saath connect karta hai: agar profile me Job
    Description di gayi hai, to us resume ka JD-match % nikaal ke
    combined_score banata hai — ATS aur JD match ka weightage ab
    hardcoded (50/50) nahi, balki HR ne is profile me khud jo
    ats_weight / jd_weight fill kiya hai wahi use hota hai. Agar JD
    nahi di gayi, to combined_score ATS score jaisa hi rehta hai.
    """

    job_description = profile.job_description

    if job_description and job_description.strip():

        jd_result = jd_matching_service.analyze(
            resume_skills=resume_skills,
            jd_text=job_description
        )

        ats_weight = profile.ats_weight if profile.ats_weight is not None else 50
        jd_weight = profile.jd_weight if profile.jd_weight is not None else 50

        resume.jd_match_score = int(jd_result["matching_score"])
        resume.jd_matched_skills = json.dumps(jd_result["matched_skills"], ensure_ascii=False)
        resume.jd_missing_skills = json.dumps(jd_result["missing_skills"], ensure_ascii=False)

        # Combined score nikalte waqt hi weights ka ratio nikalte hain
        # (total 100 na ho tab bhi) — is se profile me saved
        # ats_weight/jd_weight kabhi bhi badalte/reset nahi hote,
        # sirf calculation ke liye unka proportion use hota hai.
        total_weight = ats_weight + jd_weight
        if total_weight <= 0:
            ats_ratio, jd_ratio = 0.5, 0.5
        else:
            ats_ratio = ats_weight / total_weight
            jd_ratio = jd_weight / total_weight

        resume.combined_score = round(
            ((resume.ats_score or 0) * ats_ratio)
            + (resume.jd_match_score * jd_ratio)
        )

    else:
        resume.jd_match_score = None
        resume.jd_matched_skills = None
        resume.jd_missing_skills = None
        resume.combined_score = resume.ats_score or 0


# ===================================================
# Delete a single candidate's resume from a profile
# ===================================================

@router.post("/profile/{profile_id}/resume/{resume_id}/delete")
def delete_candidate_resume(
    profile_id: int,
    resume_id: int,
    db: Session = Depends(get_db),
    user=Depends(hr_required)
):
    # Pehle confirm karo ye profile isi HR ki hai
    profile = _get_owned_profile(db, profile_id, user.id)

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.hr_profile_id == profile.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # PDF file ko disk se bhi delete kar do
    FileService.delete_file(resume.filepath)

    db.delete(resume)
    db.commit()

    # Ek resume hatne ke baad baaki candidates ki
    # ranking/shortlisting dobara calculate karo
    HRService.recalculate_shortlist(db, profile.id)

    return RedirectResponse(
        url=f"/hr/profile/{profile.id}",
        status_code=status.HTTP_303_SEE_OTHER
    )