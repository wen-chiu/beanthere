# app/models/trip.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    destination = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    total_budget = Column(Numeric(10, 2), nullable=True)
    status = Column(String, default="active")  # active, completed, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    creator = relationship("User", back_populates="created_trips")
    members = relationship(
        "TripMember", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship(
        "Expense", back_populates="trip", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="trip")


class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    nickname = Column(String, nullable=True)  # 在此次旅行中的暱稱
    role = Column(String, default="member")  # admin, member
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
    expense_participations = relationship(
        "ExpenseParticipant", back_populates="member")
