# app/schemas/expense.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# 支出參與者模型
class ExpenseParticipantBase(BaseModel):
    member_id: int
    share_amount: Decimal
    share_ratio: Decimal = Decimal('1.0')
    is_involved: bool = True


class ExpenseParticipantCreate(ExpenseParticipantBase):
    pass


class ExpenseParticipantResponse(ExpenseParticipantBase):
    id: int
    member: Optional[dict] = None

    class Config:
        from_attributes = True


# 支出模型
class ExpenseBase(BaseModel):
    amount: Decimal
    description: str
    category: Optional[str] = None
    note: Optional[str] = None
    expense_date: datetime
    location: Optional[str] = None
    currency: str = "TWD"
    exchange_rate: Decimal = Decimal('1.0')
    is_shared: bool = True


class ExpenseCreate(ExpenseBase):
    trip_id: int
    payer_id: int
    participants: List[ExpenseParticipantCreate] = []

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('金額必須大於 0')
        return v

    @validator('participants')
    def validate_participants(cls, v, values):
        if not v and values.get('is_shared', True):
            raise ValueError('共同支出必須指定參與者')
        return v


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None
    expense_date: Optional[datetime] = None
    location: Optional[str] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    is_shared: Optional[bool] = None
    participants: Optional[List[ExpenseParticipantCreate]] = None


class ExpenseResponse(ExpenseBase):
    id: int
    trip_id: int
    payer_id: int
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    payer: UserResponse
    participants: List[ExpenseParticipantResponse] = []

    class Config:
        from_attributes = True
