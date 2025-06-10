# app/models/settlement.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    settlement_date = Column(DateTime(timezone=True),
                             server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")  # pending, completed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    trip = relationship("Trip", back_populates="settlements")
    transactions = relationship(
        "SettlementTransaction", back_populates="settlement", cascade="all, delete-orphan")


class SettlementTransaction(Base):
    __tablename__ = "settlement_transactions"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("settlements.id"))
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # 關聯
    settlement = relationship("Settlement", back_populates="transactions")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
