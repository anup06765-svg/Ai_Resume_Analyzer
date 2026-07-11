from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class JobAnalysis(Base):

    __tablename__ = "job_analysis"

    # ==========================
    # Primary Key
    # ==========================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==========================
    # Job Description
    # ==========================

    job_description = Column(
        Text,
        nullable=False
    )

    # ==========================
    # Matching Results
    # ==========================

    matching_score = Column(
        Float,
        default=0
    )

    matched_skills = Column(
        Text,
        nullable=True
    )

    missing_skills = Column(
        Text,
        nullable=True
    )

    extra_skills = Column(
        Text,
        nullable=True
    )

    ai_suggestions = Column(
        Text,
        nullable=True
    )

    # ==========================
    # Relationships
    # ==========================

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume = relationship(
        "Resume",
        backref="job_analyses"
    )

    user = relationship(
        "User",
        backref="job_analyses"
    )

    # ==========================
    # Timestamp
    # ==========================

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )