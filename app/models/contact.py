from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database.database import Base


class ContactMessage(Base):

    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    email = Column(String(150), nullable=False)

    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    