# app/schemas/trip.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# 基礎用戶模型
class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    line_user_id: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 旅行成員模型
class TripMemberBase(BaseModel):
    nickname: Optional[str] = None
    role: str = "member"


class TripMemberCreate(TripMemberBase):
    user_id: Optional[int] = None
    name: Optional[str] = None  # 如果是新用戶
    line_user_id: Optional[str] = None


class TripMemberResponse(TripMemberBase):
    id: int
    user_id: int
    user: UserResponse
    joined_at: datetime

    class Config:
        from_attributes = True


# 旅行模型
class TripBase(BaseModel):
    name: str
    description: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_budget: Optional[Decimal] = None


class TripCreate(TripBase):
    creator_id: int

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('結束日期必須在開始日期之後')
        return v


class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_budget: Optional[Decimal] = None
    status: Optional[str] = None


class TripResponse(TripBase):
    id: int
    creator_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator: UserResponse
    members: List[TripMemberResponse] = []

    class Config:
        from_attributes = True
