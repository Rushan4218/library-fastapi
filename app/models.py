from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class BookStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"


class BorrowStatus(str, enum.Enum):
    PENDING_PICKUP = "PENDING_PICKUP"
    FULFILLED = "FULFILLED"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"


def utc_now():
    return datetime.now(timezone.utc)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    isbn = Column(String(50), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    status = Column(String(50), nullable=False, default=BookStatus.AVAILABLE.value)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationship to borrow records
    borrow_records = relationship("BorrowRecord", back_populates="book", cascade="all, delete-orphan")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(50), unique=True, nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    
    # User Details
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False, index=True)
    user_phone = Column(String(50), nullable=False)
    user_address = Column(Text, nullable=False)

    status = Column(String(50), nullable=False, default=BorrowStatus.PENDING_PICKUP.value)
    borrowed_at = Column(DateTime(timezone=True), default=utc_now)
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to book
    book = relationship("Book", back_populates="borrow_records")
