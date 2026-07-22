from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.hr_profile import HRProfile


# Fallback threshold — sirf tab use hota hai jab kisi wajah se
# profile hi na mile. Normally har HR profile apna khud ka
# shortlist_threshold set karta hai (HR khud fill karta hai),
# isliye ab ye ek global hardcoded rule nahi hai.
DEFAULT_SHORTLIST_SCORE_THRESHOLD = 70


class HRService:

    @staticmethod
    def recalculate_shortlist(db: Session, hr_profile_id: int):
        """
        Ek HR profile ke saare resumes ko combined score ke
        hisaab se top -> bottom sort karta hai, aur jis kisi ka
        bhi combined score us profile ke apne shortlist_threshold
        (jo HR ne khud profile banate/edit karte waqt set kiya hai)
        ya usse zyada hai use "Shortlisted" mark kar deta hai —
        candidates ki total sankhya se koi fark nahi padta.
        """

        profile = (
            db.query(HRProfile)
            .filter(HRProfile.id == hr_profile_id)
            .first()
        )

        threshold = (
            profile.shortlist_threshold
            if profile and profile.shortlist_threshold is not None
            else DEFAULT_SHORTLIST_SCORE_THRESHOLD
        )

        resumes = (
            db.query(Resume)
            .filter(Resume.hr_profile_id == hr_profile_id)
            .all()
        )

        # Combined score (HR ke set kiye hue ATS/JD weightage se bana) se rank karte hain
        resumes.sort(
            key=lambda r: (r.combined_score or r.ats_score or 0),
            reverse=True
        )

        for resume in resumes:
            score = resume.combined_score or resume.ats_score or 0
            resume.is_shortlisted = score >= threshold

        db.commit()

        return resumes
