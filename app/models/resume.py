from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    filepath = Column(String(500), nullable=False)

    parsed_text = Column(Text, nullable=True)

    # ==========================
    # AI Analysis
    # ==========================

    ats_score = Column(Integer, default=0)

    ats_grade = Column(String(10), default="N/A")

    analysis_result = Column(Text, nullable=True)

    word_count = Column(Integer, default=0)

    matched_skills = Column(Integer, default=0)

    missing_skills = Column(Integer, default=0)

    suggestions = Column(Text, nullable=True)

    # ==========================
    # JD (Job Description) Matching - HR profile ki JD
    # se is resume ka kitna match hai
    # ==========================

    jd_match_score = Column(Integer, nullable=True)

    jd_matched_skills = Column(Text, nullable=True)

    jd_missing_skills = Column(Text, nullable=True)

    # ATS score + JD match score dono ko combine karke bana score,
    # isi se HR profile me candidates rank/shortlist hote hain
    combined_score = Column(Integer, default=0)

    # ==========================
    # User
    # ==========================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )

    # ==========================
    # HR Profile (sirf tab set hota hai jab HR ne
    # is resume ko kisi job-profile ke andar upload kiya ho)
    # ==========================

    hr_profile_id = Column(
        Integer,
        ForeignKey("hr_profiles.id"),
        nullable=True
    )

    hr_profile = relationship(
        "HRProfile",
        back_populates="resumes"
    )

    # Candidate ka naam
    candidate_name = Column(String(150), nullable=True)

    # Top scorers ko automatically shortlist karne ke liye flag
    is_shortlisted = Column(Boolean, default=False, nullable=False)