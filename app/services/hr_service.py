from sqlalchemy.orm import Session

from app.models.resume import Resume


# Is score (ya usse zyada) wale candidates seedhe Shortlisted
# mark ho jaate hain — chahe kitne bhi resumes ho ya total
# candidates ki sankhya kuch bhi ho
SHORTLIST_SCORE_THRESHOLD = 70


class HRService:

    @staticmethod
    def recalculate_shortlist(db: Session, hr_profile_id: int):
        """
        Ek HR profile ke saare resumes ko combined score ke
        hisaab se top -> bottom sort karta hai, aur jis kisi ka
        bhi combined score SHORTLIST_SCORE_THRESHOLD (70) ya
        usse zyada hai use "Shortlisted" mark kar deta hai —
        candidates ki total sankhya se koi fark nahi padta.
        """

        resumes = (
            db.query(Resume)
            .filter(Resume.hr_profile_id == hr_profile_id)
            .all()
        )

        # Combined score (50% ATS + 50% JD match) se rank karte hain
        resumes.sort(
            key=lambda r: (r.combined_score or r.ats_score or 0),
            reverse=True
        )

        for resume in resumes:
            score = resume.combined_score or resume.ats_score or 0
            resume.is_shortlisted = score >= SHORTLIST_SCORE_THRESHOLD

        db.commit()

        return resumes