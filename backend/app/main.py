# ===== Backend API (FastAPI) =====
# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from config.database import get_db, engine
from models import models
from schemas import trip_schemas, expense_schemas
from services import trip_service, expense_service, settlement_service

# Create Database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BeanThere API", version="1.0.0")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== API Routing =====

# Trips
@app.post("/api/trips", response_model=trip_schemas.Trip)
def create_trip(trip: trip_schemas.TripCreate, db: Session = Depends(get_db)):
    return trip_service.create_trip(db, trip)

@app.get("/api/trips", response_model=List[trip_schemas.Trip])
def get_trips(db: Session = Depends(get_db)):
    return trip_service.get_trips(db)

@app.get("/api/trips/{trip_id}", response_model=trip_schemas.TripDetail)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = trip_service.get_trip_detail(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

# Members
@app.post("/api/trips/{trip_id}/members")
def add_member(trip_id: int, member: trip_schemas.MemberCreate, db: Session = Depends(get_db)):
    return trip_service.add_member(db, trip_id, member)

# Expense
@app.post("/api/expenses", response_model=expense_schemas.Expense)
def create_expense(expense: expense_schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return expense_service.create_expense(db, expense)

@app.get("/api/trips/{trip_id}/expenses", response_model=List[expense_schemas.Expense])
def get_trip_expenses(trip_id: int, db: Session = Depends(get_db)):
    return expense_service.get_trip_expenses(db, trip_id)

# Settlement 
@app.get("/api/trips/{trip_id}/settlement")
def calculate_settlement(trip_id: int, db: Session = Depends(get_db)):
    return settlement_service.calculate_settlement(db, trip_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)