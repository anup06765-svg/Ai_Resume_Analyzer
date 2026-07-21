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