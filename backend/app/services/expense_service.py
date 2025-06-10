# app/services/expense_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.expense import Expense, ExpenseParticipant
from app.models.trip import TripMember
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from typing import List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ExpenseService:

    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """創建新支出記錄"""
        # 創建支出記錄
        db_expense = Expense(
            trip_id=expense_data.trip_id,
            payer_id=expense_data.payer_id,
            amount=expense_data.amount,
            description=expense_data.description,
            category=expense_data.category,
            note=expense_data.note,
            expense_date=expense_data.expense_date,
            location=expense_data.location,
            currency=expense_data.currency,
            exchange_rate=expense_data.exchange_rate,
            is_shared=expense_data.is_shared
        )

        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)

        # 如果是共同支出，添加參與者
        if expense_data.is_shared and expense_data.participants:
            for participant_data in expense_data.participants:
                db_participant = ExpenseParticipant(
                    expense_id=db_expense.id,
                    member_id=participant_data.member_id,
                    share_amount=participant_data.share_amount,
                    share_ratio=participant_data.share_ratio,
                    is_involved=participant_data.is_involved
                )
                db.add(db_participant)

        elif expense_data.is_shared:
            # 如果沒有指定參與者，自動分攤給所有成員
            ExpenseService._auto_distribute_expense(db, db_expense)

        db.commit()
        return db_expense

    @staticmethod
    def _auto_distribute_expense(db: Session, expense: Expense):
        """自動將支出平均分攤給所有旅行成員"""
        members = db.query(TripMember).filter(
            TripMember.trip_id == expense.trip_id).all()

        if not members:
            return

        share_amount = expense.amount / len(members)
        share_ratio = Decimal('1.0') / len(members)

        for member in members:
            db_participant = ExpenseParticipant(
                expense_id=expense.id,
                member_id=member.id,
                share_amount=share_amount,
                share_ratio=share_ratio,
                is_involved=True
            )
            db.add(db_participant)

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """根據 ID 獲取支出記錄"""
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @staticmethod
    def get_expenses_by_trip(db: Session, trip_id: int) -> List[Expense]:
        """獲取旅行的所有支出"""
        return db.query(Expense).filter(Expense.trip_id == trip_id).order_by(Expense.expense_date.desc()).all()

    @staticmethod
    def update_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate) -> Optional[Expense]:
        """更新支出記錄"""
        db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not db_expense:
            return None

        update_data = expense_data.dict(exclude_unset=True)
        participants_data = update_data.pop('participants', None)

        # 更新基本資訊
        for field, value in update_data.items():
            setattr(db_expense, field, value)

        # 更新參與者資訊
        if participants_data is not None:
            # 刪除現有參與者
            db.query(ExpenseParticipant).filter(
                ExpenseParticipant.expense_id == expense_id).delete()

            # 添加新參與者
            for participant_data in participants_data:
                db_participant = ExpenseParticipant(
                    expense_id=expense_id,
                    member_id=participant_data.member_id,
                    share_amount=participant_data.share_amount,
                    share_ratio=participant_data.share_ratio,
                    is_involved=participant_data.is_involved
                )
                db.add(db_participant)

        db.commit()
        db.refresh(db_expense)
        return db_expense

    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """刪除支出記錄"""
        db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not db_expense:
            return False

        db.delete(db_expense)
        db.commit()
        return True

    @staticmethod
    def get_expenses_by_category(db: Session, trip_id: int) -> dict:
        """按分類統計支出"""
        expenses = ExpenseService.get_expenses_by_trip(db, trip_id)

        category_stats = {}
        for expense in expenses:
            category = expense.category or "其他"
            if category not in category_stats:
                category_stats[category] = {
                    "amount": Decimal('0'),
                    "count": 0,
                    "expenses": []
                }

            category_stats[category]["amount"] += expense.amount
            category_stats[category]["count"] += 1
            category_stats[category]["expenses"].append(expense)

        return category_stats


# 創建全局服務實例
expense_service = ExpenseService()
