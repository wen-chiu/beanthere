from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
from typing import List, Optional
from datetime import datetime
import logging

# 配置和模型導入
from app.config.database import get_db, engine, Base
from app.config.settings import settings
from app.models import user, trip, expense, settlement
from app.schemas import trip as trip_schema, expense as expense_schema
from app.services import trip_service, expense_service, settlement_service

# 創建資料庫表
Base.metadata.create_all(bind=engine)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    description="BeanThere 旅遊分帳系統 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境需限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康檢查端點


@app.get("/")
async def root():
    return {"message": "BeanThere API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ==================== 旅行管理 API ====================


@app.post("/api/trips", response_model=trip_schema.TripResponse)
async def create_trip(
    trip_data: trip_schema.TripCreate,
    db: Session = Depends(get_db)
):
    """創建新旅行"""
    try:
        new_trip = trip_service.create_trip(db, trip_data)
        logger.info(f"Created trip: {new_trip.id}")
        return new_trip
    except Exception as e:
        logger.error(f"Error creating trip: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips", response_model=List[trip_schema.TripResponse])
async def get_trips(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取旅行列表"""
    try:
        trips = trip_service.get_trips(db, user_id)
        return trips
    except Exception as e:
        logger.error(f"Error fetching trips: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}", response_model=trip_schema.TripResponse)
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """獲取特定旅行詳情"""
    try:
        trip_data = trip_service.get_trip_by_id(db, trip_id)
        if not trip_data:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 旅伴管理 API ====================


@app.post("/api/trips/{trip_id}/members")
async def add_trip_member(
    trip_id: int,
    member_data: trip_schema.TripMemberCreate,
    db: Session = Depends(get_db)
):
    """添加旅伴"""
    try:
        member = trip_service.add_trip_member(db, trip_id, member_data)
        logger.info(f"Added member to trip {trip_id}: {member.user_id}")
        return {"message": "Member added successfully", "member": member}
    except Exception as e:
        logger.error(f"Error adding member to trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}/members")
async def get_trip_members(trip_id: int, db: Session = Depends(get_db)):
    """獲取旅行成員列表"""
    try:
        members = trip_service.get_trip_members(db, trip_id)
        return {"members": members}
    except Exception as e:
        logger.error(f"Error fetching members for trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 記帳管理 API ====================


@app.post("/api/expenses", response_model=expense_schema.ExpenseResponse)
async def create_expense(
    expense_data: expense_schema.ExpenseCreate,
    db: Session = Depends(get_db)
):
    """創建新支出記錄"""
    try:
        new_expense = expense_service.create_expense(db, expense_data)
        logger.info(f"Created expense: {new_expense.id}")
        return new_expense
    except Exception as e:
        logger.error(f"Error creating expense: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}/expenses", response_model=List[expense_schema.ExpenseResponse])
async def get_trip_expenses(trip_id: int, db: Session = Depends(get_db)):
    """獲取旅行的所有支出"""
    try:
        expenses = expense_service.get_expenses_by_trip(db, trip_id)
        return expenses
    except Exception as e:
        logger.error(f"Error fetching expenses for trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/expenses/{expense_id}", response_model=expense_schema.ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: expense_schema.ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """更新支出記錄"""
    try:
        updated_expense = expense_service.update_expense(
            db, expense_id, expense_data)
        if not updated_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        logger.info(f"Updated expense: {expense_id}")
        return updated_expense
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating expense {expense_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """刪除支出記錄"""
    try:
        success = expense_service.delete_expense(db, expense_id)
        if not success:
            raise HTTPException(status_code=404, detail="Expense not found")
        logger.info(f"Deleted expense: {expense_id}")
        return {"message": "Expense deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting expense {expense_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 分帳計算 API ====================


@app.get("/api/trips/{trip_id}/settlement")
async def calculate_settlement(trip_id: int, db: Session = Depends(get_db)):
    """計算旅行分帳結果"""
    try:
        settlement_result = settlement_service.calculate_settlement(
            db, trip_id)
        logger.info(f"Calculated settlement for trip: {trip_id}")
        return settlement_result
    except Exception as e:
        logger.error(
            f"Error calculating settlement for trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/trips/{trip_id}/settlement/finalize")
async def finalize_settlement(trip_id: int, db: Session = Depends(get_db)):
    """確認並保存分帳結果"""
    try:
        result = settlement_service.finalize_settlement(db, trip_id)
        logger.info(f"Finalized settlement for trip: {trip_id}")
        return {"message": "Settlement finalized", "settlement_id": result.id}
    except Exception as e:
        logger.error(
            f"Error finalizing settlement for trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== OCR 上傳 API ====================


@app.post("/api/ocr/upload")
async def upload_receipt_for_ocr(
    file: bytes,
    trip_id: int,
    db: Session = Depends(get_db)
):
    """上傳收據進行 OCR 識別"""
    try:
        # 這裡會調用 OCR 服務
        # ocr_result = ocr_service.process_receipt(file)

        # 暫時返回模擬結果
        mock_result = {
            "amount": 850.0,
            "merchant": "7-ELEVEN",
            "date": "2024-12-07",
            "items": ["咖啡", "三明治", "飲料"],
            "confidence": 0.85
        }

        logger.info(f"OCR processed for trip: {trip_id}")
        return {"ocr_result": mock_result, "message": "OCR processing completed"}
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 報表 API ====================


@app.get("/api/trips/{trip_id}/report")
async def get_trip_report(trip_id: int, db: Session = Depends(get_db)):
    """獲取旅行消費報表"""
    try:
        # 獲取支出統計
        expenses = expense_service.get_expenses_by_trip(db, trip_id)

        # 計算分類統計
        category_stats = {}
        total_amount = 0

        for expense in expenses:
            category = expense.category or "其他"
            if category not in category_stats:
                category_stats[category] = {"amount": 0, "count": 0}
            category_stats[category]["amount"] += expense.amount
            category_stats[category]["count"] += 1
            total_amount += expense.amount

        # 計算百分比
        for category in category_stats:
            category_stats[category]["percentage"] = round(
                (category_stats[category]["amount"] / total_amount) * 100, 2
            ) if total_amount > 0 else 0

        report = {
            "trip_id": trip_id,
            "total_amount": total_amount,
            "total_expenses": len(expenses),
            "category_breakdown": category_stats,
            "daily_spending": []  # 可以進一步實現按日統計
        }

        logger.info(f"Generated report for trip: {trip_id}")
        return report
    except Exception as e:
        logger.error(f"Error generating report for trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 錯誤處理 ====================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
