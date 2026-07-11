from sqlalchemy import Column, Integer, String, Text, ForeignKey
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