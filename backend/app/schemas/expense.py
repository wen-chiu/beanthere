from pydantic import BaseModel
from datetime import datetime
from typing import List

class ExpenseParticipantCreate(BaseModel):
    member_id: int

class ExpenseCreate(BaseModel):
    trip_id: int
    payer_id: int
    amount: float
    description: str
    category: str = "其他"
    participants: List[ExpenseParticipantCreate]

class ExpenseParticipant(BaseModel):
    member_id: int
    share_amount: float
    
    class Config:
        from_attributes = True

class Expense(BaseModel):
    id: int
    trip_id: int
    payer_id: int
    amount: float
    description: str
    category: str
    expense_date: datetime
    participants: List[ExpenseParticipant]
    
    class Config:
        from_attributes = True
