# app/schemas/settlement.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal


# 分帳交易模型
class SettlementTransactionBase(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: Decimal
    description: Optional[str] = None


class SettlementTransactionCreate(SettlementTransactionBase):
    pass


class SettlementTransactionResponse(SettlementTransactionBase):
    id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    from_user: UserResponse
    to_user: UserResponse

    class Config:
        from_attributes = True


# 分帳結果模型
class SettlementBase(BaseModel):
    total_amount: Decimal
    notes: Optional[str] = None


class SettlementCreate(SettlementBase):
    trip_id: int
    transactions: List[SettlementTransactionCreate] = []


class SettlementResponse(SettlementBase):
    id: int
    trip_id: int
    settlement_date: datetime
    status: str
    created_at: datetime
    transactions: List[SettlementTransactionResponse] = []

    class Config:
        from_attributes = True


# 分帳計算結果模型
class UserBalance(BaseModel):
    user_id: int
    name: str
    total_paid: Decimal
    total_owed: Decimal
    net_balance: Decimal  # 正數表示應收，負數表示應付


class SettlementCalculation(BaseModel):
    trip_id: int
    total_expenses: Decimal
    user_balances: List[UserBalance]
    suggested_transactions: List[SettlementTransactionBase]


# OCR 結果模型
class OCRResult(BaseModel):
    amount: Optional[Decimal] = None
    merchant: Optional[str] = None
    date: Optional[str] = None
    items: List[str] = []
    confidence: float = 0.0
    raw_text: Optional[str] = None


class OCRRequest(BaseModel):
    trip_id: int
    image_data: str  # base64 encoded image


class OCRResponse(BaseModel):
    success: bool
    result: Optional[OCRResult] = None
    error: Optional[str] = None


# 報表模型
class CategoryStats(BaseModel):
    category: str
    amount: Decimal
    count: int
    percentage: float


class DailySpending(BaseModel):
    date: str
    amount: Decimal
    expense_count: int


class TripReport(BaseModel):
    trip_id: int
    trip_name: str
    total_amount: Decimal
    total_expenses: int
    average_per_person: Decimal
    category_breakdown: List[CategoryStats]
    daily_spending: List[DailySpending]
    top_expenses: List[ExpenseResponse]
    duration_days: int
