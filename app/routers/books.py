from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.auth import get_current_admin
from app.database import get_db
from app.models import Book, BookStatus
from app.schemas import (
    BookCreate,
    BookResponse,
    BookStatusUpdate,
    BookUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["Books"])


# ------------------- PUBLIC ENDPOINTS -------------------

@router.get("/books", response_model=List[BookResponse], summary="List all books (Public)")
def get_books(
    search: Optional[str] = Query(None, description="Search term for title, author, or ISBN"),
    category: Optional[str] = Query(None, description="Filter by book category"),
    status: Optional[BookStatus] = Query(None, description="Filter by book status (AVAILABLE, BORROWED, etc.)"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Limit max returned books"),
    db: Session = Depends(get_db),
):
    """Retrieve books with optional filtering by search term, category, or status."""
    query = db.query(Book)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                Book.isbn.ilike(search_pattern),
            )
        )

    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))

    if status:
        query = query.filter(Book.status == status.value)

    books = query.order_by(Book.id.desc()).offset(skip).limit(limit).all()
    return books


@router.get("/books/{book_id}", response_model=BookResponse, summary="Get single book by ID (Public)")
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed information for a single book by its ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    return book


# ------------------- ADMIN ENDPOINTS -------------------

@router.post(
    "/admin/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book (Admin Only)",
)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Create a new book in the library collection."""
    if book_in.isbn:
        existing = db.query(Book).filter(Book.isbn == book_in.isbn).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN '{book_in.isbn}' already exists.",
            )

    new_book = Book(
        title=book_in.title,
        author=book_in.author,
        isbn=book_in.isbn,
        description=book_in.description,
        category=book_in.category,
        status=BookStatus.AVAILABLE.value,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put(
    "/admin/books/{book_id}",
    response_model=BookResponse,
    summary="Update book details (Admin Only)",
)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Update details of an existing book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    if book_in.isbn and book_in.isbn != book.isbn:
        existing = db.query(Book).filter(Book.isbn == book_in.isbn).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN '{book_in.isbn}' already exists.",
            )

    update_data = book_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.patch(
    "/admin/books/{book_id}/status",
    response_model=BookResponse,
    summary="Update book status manually (Admin Only)",
)
def update_book_status(
    book_id: int,
    status_in: BookStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Change book status (AVAILABLE, BORROWED, MAINTENANCE, RESERVED)."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    book.status = status_in.status.value
    db.commit()
    db.refresh(book)
    return book


@router.delete(
    "/admin/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book (Admin Only)",
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Delete a book from the library catalog."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    db.delete(book)
    db.commit()
    return None
