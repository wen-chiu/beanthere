from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Expense, ExpenseParticipant, TripMember
from collections import defaultdict

def calculate_settlement(db: Session, trip_id: int):
    # Get all members
    members = db.query(TripMember).filter(TripMember.trip_id == trip_id).all()
    member_dict = {m.id: m.nickname for m in members}
    
    # Calculate expenses for every members and how much to pay
    balances = defaultdict(float)
    
    # Calculate the actual should paid 
    paid_amounts = db.query(
        Expense.payer_id,
        func.sum(Expense.amount).label('total_paid')
    ).filter(
        Expense.trip_id == trip_id
    ).group_by(Expense.payer_id).all()
    
    for payer_id, total_paid in paid_amounts:
        balances[payer_id] += total_paid
    
    # Calculate the shared amounts
    shared_amounts = db.query(
        ExpenseParticipant.member_id,
        func.sum(ExpenseParticipant.share_amount).label('total_share')
    ).join(Expense).filter(
        Expense.trip_id == trip_id
    ).group_by(ExpenseParticipant.member_id).all()
    
    for member_id, total_share in shared_amounts:
        balances[member_id] -= total_share
    
    # Get the outcome
    settlements = []
    positive_balances = []
    negative_balances = []
    
    for member_id, balance in balances.items():
        member_name = member_dict.get(member_id, f"Member {member_id}")
        if balance > 0:
            positive_balances.append((member_name, balance))
        elif balance < 0:
            negative_balances.append((member_name, -balance))
    
    # Calculate who owns who
    for creditor_name, credit in positive_balances:
        for debtor_name, debt in negative_balances:
            if debt > 0 and credit > 0:
                transfer_amount = min(credit, debt)
                settlements.append({
                    "from": debtor_name,
                    "to": creditor_name,
                    "amount": transfer_amount
                })
                credit -= transfer_amount
                debt -= transfer_amount
    
    return {
        "balances": [
            {"member": name, "balance": balance}
            for member_id, balance in balances.items()
            for name in [member_dict.get(member_id, f"Member {member_id}")]
        ],
        "settlements": settlements
    }