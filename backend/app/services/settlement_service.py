# app/services/settlement_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.expense import Expense, ExpenseParticipant
from app.models.trip import TripMember
from app.models.settlement import Settlement, SettlementTransaction
from app.models.user import User
from app.schemas.settlement import SettlementCalculation, UserBalance, SettlementTransactionBase
from typing import List, Dict
from decimal import Decimal
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SettlementService:

    @staticmethod
    def calculate_settlement(db: Session, trip_id: int) -> SettlementCalculation:
        """計算旅行分帳結果"""
        # 獲取所有支出和參與者
        expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()
        members = db.query(TripMember).filter(
            TripMember.trip_id == trip_id).all()

        if not expenses or not members:
            return SettlementCalculation(
                trip_id=trip_id,
                total_expenses=Decimal('0'),
                user_balances=[],
                suggested_transactions=[]
            )

        # 計算每個用戶的支付和應付金額
        user_paid = defaultdict(Decimal)  # 每個用戶實際支付的金額
        user_owed = defaultdict(Decimal)  # 每個用戶應該分攤的金額

        total_expenses = Decimal('0')

        for expense in expenses:
            total_expenses += expense.amount
            user_paid[expense.payer_id] += expense.amount

            # 計算每個參與者應分攤的金額
            participants = db.query(ExpenseParticipant).filter(
                ExpenseParticipant.expense_id == expense.id
            ).all()

            for participant in participants:
                if participant.is_involved:
                    user_owed[participant.member.user_id] += participant.share_amount

        # 計算淨餘額
        user_balances = []
        net_balances = {}

        for member in members:
            user_id = member.user_id
            paid = user_paid.get(user_id, Decimal('0'))
            owed = user_owed.get(user_id, Decimal('0'))
            net_balance = paid - owed  # 正數表示應收，負數表示應付

            net_balances[user_id] = net_balance

            user_balances.append(UserBalance(
                user_id=user_id,
                name=member.user.name,
                total_paid=paid,
                total_owed=owed,
                net_balance=net_balance
            ))

        # 生成建議的轉帳交易
        suggested_transactions = SettlementService._generate_transactions(
            net_balances, members)

        return SettlementCalculation(
            trip_id=trip_id,
            total_expenses=total_expenses,
            user_balances=user_balances,
            suggested_transactions=suggested_transactions
        )

    @staticmethod
    def _generate_transactions(net_balances: Dict[int, Decimal], members: List[TripMember]) -> List[SettlementTransactionBase]:
        """生成最優化的轉帳建議"""
        # 分離債權人和債務人
        creditors = []  # 應收款人 (正餘額)
        debtors = []    # 應付款人 (負餘額)

        user_map = {member.user_id: member.user for member in members}

        for user_id, balance in net_balances.items():
            if balance > Decimal('0.01'):  # 避免浮點誤差
                creditors.append((user_id, balance))
            elif balance < Decimal('-0.01'):
                debtors.append((user_id, abs(balance)))

        # 使用貪心算法生成最少交易次數的方案
        transactions = []

        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):
            creditor_id, credit_amount = creditors[i]
            debtor_id, debt_amount = debtors[j]

            # 計算交易金額
            transfer_amount = min(credit_amount, debt_amount)

            if transfer_amount > Decimal('0.01'):  # 避免小額轉帳
                transactions.append(SettlementTransactionBase(
                    from_user_id=debtor_id,
                    to_user_id=creditor_id,
                    amount=transfer_amount,
                    description=f"{user_map[debtor_id].name} 轉給 {user_map[creditor_id].name}"
                ))

            # 更新餘額
            creditors[i] = (creditor_id, credit_amount - transfer_amount)
            debtors[j] = (debtor_id, debt_amount - transfer_amount)

            # 移動指針
            if creditors[i][1] <= Decimal('0.01'):
                i += 1
            if debtors[j][1] <= Decimal('0.01'):
                j += 1

        return transactions

    @staticmethod
    def finalize_settlement(db: Session, trip_id: int) -> Settlement:
        """確認並保存分帳結果"""
        # 計算分帳結果
        calculation = SettlementService.calculate_settlement(db, trip_id)

        # 創建分帳記錄
        db_settlement = Settlement(
            trip_id=trip_id,
            total_amount=calculation.total_expenses,
            status="pending"
        )

        db.add(db_settlement)
        db.commit()
        db.refresh(db_settlement)

        # 創建轉帳記錄
        for transaction in calculation.suggested_transactions:
            db_transaction = SettlementTransaction(
                settlement_id=db_settlement.id,
                from_user_id=transaction.from_user_id,
                to_user_id=transaction.to_user_id,
                amount=transaction.amount,
                description=transaction.description
            )
            db.add(db_transaction)

        db.commit()
        return db_settlement

    @staticmethod
    def get_settlement_by_trip(db: Session, trip_id: int) -> List[Settlement]:
        """獲取旅行的分帳記錄"""
        return db.query(Settlement).filter(Settlement.trip_id == trip_id).all()


# 創建全局服務實例
settlement_service = SettlementService()
