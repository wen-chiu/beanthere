from sqlalchemy.orm import Session
from models.models import Expense, ExpenseParticipant
from schemas.expense_schemas import ExpenseCreate

def create_expense(db: Session, expense: ExpenseCreate):
    # Expense record create
    db_expense = Expense(
        trip_id=expense.trip_id,
        payer_id=expense.payer_id,
        amount=expense.amount,
        description=expense.description,
        category=expense.category
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    # Split up share amount
    share_amount = expense.amount / len(expense.participants)
    
    # participant(trip members) create
    for participant in expense.participants:
        db_participant = ExpenseParticipant(
            expense_id=db_expense.id,
            member_id=participant.member_id,
            share_amount=share_amount
        )
        db.add(db_participant)
    
    db.commit()
    return db_expense

def get_trip_expenses(db: Session, trip_id: int):
    return db.query(Expense).filter(Expense.trip_id == trip_id).all()