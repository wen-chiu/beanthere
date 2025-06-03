# ===== Database Model =====
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, unique=True, index=True)
    display_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("TripMember", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")

class TripMember(Base):
    __tablename__ = "trip_members"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    nickname = Column(String)
    
    trip = relationship("Trip", back_populates="members")
    user = relationship("User")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    payer_id = Column(Integer, ForeignKey("trip_members.id"))
    amount = Column(Float)
    description = Column(String)
    category = Column(String)
    expense_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    trip = relationship("Trip", back_populates="expenses")
    payer = relationship("TripMember")
    participants = relationship("ExpenseParticipant", back_populates="expense")

class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    member_id = Column(Integer, ForeignKey("trip_members.id"))
    share_amount = Column(Float)
    
    expense = relationship("Expense", back_populates="participants")
    member = relationship("TripMember")