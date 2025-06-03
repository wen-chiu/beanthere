from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TripCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Trip(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MemberCreate(BaseModel):
    nickname: str

class Member(BaseModel):
    id: int
    nickname: str
    
    class Config:
        from_attributes = True

class TripDetail(Trip):
    members: List[Member]