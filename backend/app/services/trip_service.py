# app/services/trip_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.trip import Trip, TripMember
from app.models.user import User
from app.schemas.trip import TripCreate, TripUpdate, TripMemberCreate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TripService:
    @staticmethod
    def create_trip(db: Session, trip_data: TripCreate) -> Trip:
        """創建新旅行"""
        db_trip = Trip(
            name=trip_data.name,
            description=trip_data.description,
            destination=trip_data.destination,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            creator_id=trip_data.creator_id,
            total_budget=trip_data.total_budget
        )

        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)

        # 自動將創建者加入為管理員
        TripService.add_trip_member(
            db,
            db_trip.id,
            TripMemberCreate(user_id=trip_data.creator_id, role="admin")
        )

        return db_trip

    @staticmethod
    def get_trip_by_id(db: Session, trip_id: int) -> Optional[Trip]:
        """根據 ID 獲取旅行"""
        return db.query(Trip).filter(Trip.id == trip_id).first()

    @staticmethod
    def get_trips(db: Session, user_id: Optional[str] = None) -> List[Trip]:
        """獲取旅行列表"""
        query = db.query(Trip)

        if user_id:
            # 獲取用戶參與的旅行
            query = query.join(TripMember).filter(
                TripMember.user_id == user_id)

        return query.order_by(Trip.created_at.desc()).all()

    @staticmethod
    def update_trip(db: Session, trip_id: int, trip_data: TripUpdate) -> Optional[Trip]:
        """更新旅行資訊"""
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not db_trip:
            return None

        update_data = trip_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_trip, field, value)

        db.commit()
        db.refresh(db_trip)
        return db_trip

    @staticmethod
    def delete_trip(db: Session, trip_id: int) -> bool:
        """刪除旅行"""
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not db_trip:
            return False

        db.delete(db_trip)
        db.commit()
        return True

    @staticmethod
    def add_trip_member(db: Session, trip_id: int, member_data: TripMemberCreate) -> TripMember:
        """添加旅行成員"""
        # 如果提供了 user_id，直接使用
        if member_data.user_id:
            user_id = member_data.user_id
        else:
            # 否則根據 line_user_id 或 name 查找或創建用戶
            user = None
            if member_data.line_user_id:
                user = db.query(User).filter(User.line_user_id ==
                                             member_data.line_user_id).first()

            if not user and member_data.name:
                # 創建新用戶
                user = User(
                    name=member_data.name,
                    line_user_id=member_data.line_user_id
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            if not user:
                raise ValueError("無法找到或創建用戶")

            user_id = user.id

        # 檢查是否已經是成員
        existing = db.query(TripMember).filter(
            and_(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        ).first()

        if existing:
            raise ValueError("用戶已經是此旅行的成員")

        # 創建新成員
        db_member = TripMember(
            trip_id=trip_id,
            user_id=user_id,
            nickname=member_data.nickname,
            role=member_data.role
        )

        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_trip_members(db: Session, trip_id: int) -> List[TripMember]:
        """獲取旅行成員列表"""
        return db.query(TripMember).filter(TripMember.trip_id == trip_id).all()

    @staticmethod
    def remove_trip_member(db: Session, trip_id: int, user_id: int) -> bool:
        """移除旅行成員"""
        db_member = db.query(TripMember).filter(
            and_(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        ).first()

        if not db_member:
            return False

        db.delete(db_member)
        db.commit()
        return True


# 創建全局服務實例
trip_service = TripService()
