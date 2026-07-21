from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    email = Column(String(150), unique=True, index=True, nullable=False)

    password = Column(String(255), nullable=False)

    # -----------------------------
    # Role: "candidate" (normal user) ya "hr" (recruiter)
    # -----------------------------

    role = Column(String(20), nullable=False, default="candidate")

    # -----------------------------
    # Relationships
    # -----------------------------

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    hr_profiles = relationship(
        "HRProfile",
        back_populates="hr",
        cascade="all, delete-orphan"
    )