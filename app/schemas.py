from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import BookStatus, BorrowStatus


# ------------------- Auth Schemas -------------------

class AdminLogin(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "admin"})
    password: str = Field(..., json_schema_extra={"example": "adminsecret"})


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ------------------- Book Schemas -------------------

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "The Great Gatsby"})
    author: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "F. Scott Fitzgerald"})
    isbn: Optional[str] = Field(None, max_length=50, json_schema_extra={"example": "978-0743273565"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "A classic novel about the American Dream."})
    category: Optional[str] = Field(None, max_length=100, json_schema_extra={"example": "Fiction"})


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class BookStatusUpdate(BaseModel):
    status: BookStatus = Field(..., json_schema_extra={"example": BookStatus.AVAILABLE})


class BookResponse(BookBase):
    id: int
    status: BookStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------- Borrow Schemas -------------------

class BorrowRequest(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "John Doe"})
    user_email: EmailStr = Field(..., json_schema_extra={"example": "john.doe@example.com"})
    user_phone: str = Field(..., min_length=5, max_length=50, json_schema_extra={"example": "+1-555-0199"})
    user_address: str = Field(..., min_length=5, json_schema_extra={"example": "123 Library St, Main City"})


class BorrowResponse(BaseModel):
    token: str = Field(..., json_schema_extra={"example": "LIB-9X82-K4M1"})
    status: BorrowStatus
    book_id: int
    book_title: str
    user_name: str
    user_email: str
    user_phone: str
    user_address: str
    borrowed_at: datetime
    instructions: str = "Please present this token at the physical library front desk to pick up your book."


class BorrowRecordResponse(BaseModel):
    id: int
    token: str
    book_id: int
    user_name: str
    user_email: str
    user_phone: str
    user_address: str
    status: BorrowStatus
    borrowed_at: datetime
    fulfilled_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    book: Optional[BookResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TokenVerifyResponse(BaseModel):
    valid: bool
    token: str
    status: BorrowStatus
    book: BookResponse
    borrower_name: str
    borrower_email: str
    borrowed_at: datetime
    fulfilled_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
