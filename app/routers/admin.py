from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.auth import get_current_admin
from app.database import get_db
from app.models import Book, BookStatus, BorrowRecord, BorrowStatus
from app.schemas import BorrowRecordResponse

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Borrowing Management"])


@router.get(
    "/borrowing-history",
    response_model=List[BorrowRecordResponse],
    summary="View complete borrowing history (Admin Only)",
)
def get_borrowing_history(
    status: Optional[BorrowStatus] = Query(None, description="Filter by status (PENDING_PICKUP, FULFILLED, RETURNED, CANCELLED)"),
    token: Optional[str] = Query(None, description="Filter by pick-up token"),
    user_email: Optional[str] = Query(None, description="Filter by borrower email"),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Retrieve full borrowing history with optional filters."""
    query = db.query(BorrowRecord).options(joinedload(BorrowRecord.book))

    if status:
        query = query.filter(BorrowRecord.status == status.value)
    if token:
        query = query.filter(BorrowRecord.token == token.upper())
    if user_email:
        query = query.filter(BorrowRecord.user_email.ilike(f"%{user_email}%"))
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)

    records = query.order_by(BorrowRecord.id.desc()).offset(skip).limit(limit).all()
    return records


@router.patch(
    "/borrowing-history/{record_id}/fulfill",
    response_model=BorrowRecordResponse,
    summary="Mark token pickup as fulfilled (Admin Only)",
)
def fulfill_pickup(
    record_id: int,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Mark physical pickup as completed when user presents token at library."""
    record = db.query(BorrowRecord).options(joinedload(BorrowRecord.book)).filter(BorrowRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrow record with ID {record_id} not found",
        )

    if record.status == BorrowStatus.FULFILLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow record is already marked as fulfilled.",
        )

    if record.status == BorrowStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot fulfill a record that has already been returned.",
        )

    record.status = BorrowStatus.FULFILLED.value
    record.fulfilled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(record)
    return record


@router.patch(
    "/borrowing-history/{record_id}/return",
    response_model=BorrowRecordResponse,
    summary="Process book return (Admin Only)",
)
def return_borrowed_book(
    record_id: int,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Process return of borrowed book.
    
    - Marks borrow record as RETURNED.
    - Sets returned timestamp.
    - Resets book status back to AVAILABLE.
    """
    record = db.query(BorrowRecord).options(joinedload(BorrowRecord.book)).filter(BorrowRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrow record with ID {record_id} not found",
        )

    if record.status == BorrowStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has already been returned for this record.",
        )

    # 1. Update borrow record status
    record.status = BorrowStatus.RETURNED.value
    record.returned_at = datetime.now(timezone.utc)

    # 2. Reset associated book status to AVAILABLE
    if record.book:
        record.book.status = BookStatus.AVAILABLE.value

    db.commit()
    db.refresh(record)
    return record
