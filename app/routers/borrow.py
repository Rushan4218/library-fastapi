from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Book, BookStatus, BorrowRecord, BorrowStatus
from app.schemas import BorrowRequest, BorrowResponse, TokenVerifyResponse
from app.utils import generate_pickup_token

router = APIRouter(prefix="/api/v1", tags=["Borrowing (User)"])


@router.post(
    "/books/{book_id}/borrow",
    response_model=BorrowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book online (User)",
)
def borrow_book(
    book_id: int,
    borrow_in: BorrowRequest,
    db: Session = Depends(get_db),
):
    """Borrow a book online by providing user contact details.
    
    - Marks book status as BORROWED immediately.
    - Generates a unique pick-up token for physical library retrieval.
    """
    # 1. Fetch book with lock/check
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} does not exist",
        )

    # 2. Check if available
    if book.status != BookStatus.AVAILABLE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book '{book.title}' is currently not available for borrowing (Status: {book.status})",
        )

    # 3. Generate unique token
    token = generate_pickup_token()
    while db.query(BorrowRecord).filter(BorrowRecord.token == token).first():
        token = generate_pickup_token()

    # 4. Mark book as BORROWED
    book.status = BookStatus.BORROWED.value

    # 5. Create borrowing record
    record = BorrowRecord(
        token=token,
        book_id=book.id,
        user_name=borrow_in.user_name,
        user_email=borrow_in.user_email,
        user_phone=borrow_in.user_phone,
        user_address=borrow_in.user_address,
        status=BorrowStatus.PENDING_PICKUP.value,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return BorrowResponse(
        token=token,
        status=BorrowStatus(record.status),
        book_id=book.id,
        book_title=book.title,
        user_name=record.user_name,
        user_email=record.user_email,
        user_phone=record.user_phone,
        user_address=record.user_address,
        borrowed_at=record.borrowed_at,
    )


@router.get(
    "/borrow/verify/{token}",
    response_model=TokenVerifyResponse,
    summary="Verify a pick-up token (Public/Staff)",
)
def verify_pickup_token(token: str, db: Session = Depends(get_db)):
    """Verify validity and details of a pick-up token."""
    record = db.query(BorrowRecord).filter(BorrowRecord.token == token.upper()).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick-up token '{token}' is invalid or not found",
        )

    return TokenVerifyResponse(
        valid=True,
        token=record.token,
        status=BorrowStatus(record.status),
        book=record.book,
        borrower_name=record.user_name,
        borrower_email=record.user_email,
        borrowed_at=record.borrowed_at,
        fulfilled_at=record.fulfilled_at,
        returned_at=record.returned_at,
    )
