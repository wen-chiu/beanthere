# app/models/journal.py (預留給日記功能)
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    journal_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    weather = Column(String, nullable=True)
    mood = Column(String, nullable=True)
    photos = Column(Text, nullable=True)  # JSON array of photo URLs
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯 (預留)
    # trip = relationship("Trip")
    # author = relationship("User")
