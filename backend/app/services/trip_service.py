from sqlalchemy.orm import Session
from models.models import Trip, TripMember, User
from schemas.trip_schemas import TripCreate, MemberCreate

def create_trip(db: Session, trip: TripCreate):
    db_trip = Trip(**trip.dict())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trips(db: Session):
    return db.query(Trip).all()

def get_trip_detail(db: Session, trip_id: int):
    return db.query(Trip).filter(Trip.id == trip_id).first()

def add_member(db: Session, trip_id: int, member: MemberCreate):
    db_member = TripMember(trip_id=trip_id, nickname=member.nickname)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member