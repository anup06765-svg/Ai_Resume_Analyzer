from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class HRProfile(Base):
    """
    Ek HR "Job Profile" / "Hiring Batch" hai.
    Example: "Backend Developer - Aug Batch".

    HR isi profile ke andar bahut saare resumes (10, 20, 50...)
    upload karta hai. Sab resumes isi profile se link hote hain,
    taaki HR sirf apni profile ke candidates hi dekh sake.
    """

    __tablename__ = "hr_profiles"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    job_description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ==========================
    # HR-configurable shortlisting settings
    # (pehle ye sab hardcoded the — ab har profile ke liye
    # HR khud apni marzi se ye values set kar sakta hai)
    # ==========================

    # Kitna Combined Score chahiye taaki candidate seedhe
    # "Shortlisted" mark ho jaaye (pehle hardcoded 70 tha)
    shortlist_threshold = Column(Integer, default=70, nullable=False)

    # Combined Score banane me ATS score aur JD Match score ka
    # kitna weightage (%) rahega (pehle hardcoded 50/50 tha)
    ats_weight = Column(Integer, default=50, nullable=False)
    jd_weight = Column(Integer, default=50, nullable=False)

    # ==========================
    # Owner (HR user)
    # ==========================

    hr_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    hr = relationship(
        "User",
        back_populates="hr_profiles"
    )

    # ==========================
    # Resumes uploaded under this profile
    # ==========================

    resumes = relationship(
        "Resume",
        back_populates="hr_profile",
        cascade="all, delete-orphan"
    )