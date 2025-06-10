# app/models/expense.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    payer_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=True)  # 交通, 住宿, 餐飲, 娛樂, 購物, 其他
    note = Column(Text, nullable=True)
    expense_date = Column(DateTime, nullable=False)
    receipt_url = Column(String, nullable=True)  # 收據圖片 URL
    is_shared = Column(Boolean, default=True)  # 是否為共同支出
    location = Column(String, nullable=True)  # 消費地點
    currency = Column(String, default="TWD")
    exchange_rate = Column(Numeric(10, 4), default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    trip = relationship("Trip", back_populates="expenses")
    payer = relationship("User", back_populates="expenses")
    participants = relationship(
        "ExpenseParticipant", back_populates="expense", cascade="all, delete-orphan")


class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    member_id = Column(Integer, ForeignKey("trip_members.id"))
    share_amount = Column(Numeric(10, 2), nullable=False)  # 此人應分攤的金額
    share_ratio = Column(Numeric(5, 4), default=1.0)  # 分攤比例 (0.0-1.0)
    is_involved = Column(Boolean, default=True)  # 是否參與此筆消費

    # 關聯
    expense = relationship("Expense", back_populates="participants")
    member = relationship(
        "TripMember", back_populates="expense_participations")
