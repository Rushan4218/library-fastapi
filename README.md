# 📚 FastAPI Library Management Backend

A lightweight, robust, and asynchronous RESTful API built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**. Designed for quick testing and seamless integration with front-end applications like **Next.js**.

---

## 🌟 Features Overview

- 🔐 **Environment-Based Admin Auth**: No complex user tables needed. Admin credentials are set via environment variables and authenticated using signed JWT bearer tokens.
- 📖 **Complete Book Catalog Management**: Public book listings, searching, filtering, and single-item detail endpoints; Admin CRUD operations & status updates (`AVAILABLE`, `BORROWED`, `MAINTENANCE`, `RESERVED`).
- 🎟️ **Online Book Borrowing & Pick-up Token**: Users borrow books by submitting contact details (`name`, `email`, `phone`, `address`). The book is immediately marked as `BORROWED` and a unique pick-up token (e.g. `LIB-8F3A-9B2C`) is generated for physical library pickup.
- 🔍 **Token Verification**: Public/Staff endpoint to verify token validity, borrower info, and fulfillment status.
- 📋 **Admin Borrowing History & Returns**: Full audit trail of borrowings. Admins can mark pickups as fulfilled and process book returns (which automatically resets book availability).
- ⚡ **Next.js & AI Frontend Ready**: CORS enabled, interactive Swagger UI documentation (`/docs`), and full TypeScript-ready JSON payload specifications below.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology |
| :--- | :--- |
| **Framework** | FastAPI (Python 3.10+) |
| **ASGI Server** | Uvicorn |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 |
| **Data Validation** | Pydantic v2 |
| **Authentication** | JWT (PyJWT / python-jose) + OAuth2 Bearer |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
Ensure Python 3.10+ and PostgreSQL are installed and running.

### 2. Clone & Environment Configuration
Copy the sample environment file and update your PostgreSQL database URL and admin credentials:

```bash
cp .env.example .env
```

`.env` configuration file:
```env
# PostgreSQL Database Connection URL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/library_db

# Admin Credentials (Set your preferred admin login here)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=adminsecret

# Security Settings
SECRET_KEY=e839174fb2461d31a55b1bf185c6b907c08e5e89d150244f71a933f7c46ef85d
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Installation
Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Running the Server
Start the development server with auto-reload:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

---

## 📖 Interactive OpenAPI / Swagger Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🗄️ Database Schema Summary

### `books` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Primary key |
| `title` | String(255) | Indexed, Not Null | Book title |
| `author` | String(255) | Not Null | Author name |
| `isbn` | String(50) | Unique, Optional | International Standard Book Number |
| `description`| Text | Optional | Synopsis/Summary |
| `category` | String(100) | Indexed, Optional | Genre/Category |
| `status` | String(50) | Not Null, Default `AVAILABLE` | Status: `AVAILABLE`, `BORROWED`, `MAINTENANCE`, `RESERVED` |
| `created_at` | DateTime | Auto UTC timestamp | Creation time |
| `updated_at` | DateTime | Auto UTC timestamp | Last update time |

### `borrow_records` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Primary key |
| `token` | String(50) | Unique, Indexed, Not Null | Pick-up token (e.g. `LIB-8F3A-9B2C`) |
| `book_id` | Integer | FK -> `books.id` | Foreign Key to Book |
| `user_name` | String(255) | Not Null | Borrower's full name |
| `user_email` | String(255) | Indexed, Not Null | Borrower's email address |
| `user_phone` | String(50) | Not Null | Borrower's contact phone number |
| `user_address`| Text | Not Null | Borrower's delivery/home address |
| `status` | String(50) | Not Null, Default `PENDING_PICKUP` | Status: `PENDING_PICKUP`, `FULFILLED`, `RETURNED`, `CANCELLED` |
| `borrowed_at`| DateTime | Auto UTC timestamp | Time request was made |
| `fulfilled_at`| DateTime | Optional | Timestamp when admin verified pickup |
| `returned_at`| DateTime | Optional | Timestamp when book was returned |

---

## 📡 API Endpoints Reference (For Next.js / Frontend AI Developers)

### Base URL: `http://localhost:8000/api/v1`

---

### 1. Admin Authentication

#### `POST /auth/login` (Form-Data) or `POST /auth/login/json` (JSON Body)
Used by Admin to acquire a Bearer JWT token.

**JSON Request Body (`POST /api/v1/auth/login/json`):**
```json
{
  "username": "admin",
  "password": "adminsecret"
}
```

**Success Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> **Note**: For subsequent Admin endpoints, include the header:
> `Authorization: Bearer <access_token>`

---

### 2. Public / User Book Endpoints

#### `GET /books`
List all books with pagination and optional filters.

**Query Parameters:**
- `search` (optional string): Search title, author, or ISBN.
- `category` (optional string): Filter by genre/category.
- `status` (optional string): `AVAILABLE`, `BORROWED`, etc.
- `skip` (int, default `0`): Pagination offset.
- `limit` (int, default `50`): Max items per page.

**Response (`200 OK`):**
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "description": "A Handbook of Agile Software Craftsmanship",
    "category": "Technology",
    "status": "AVAILABLE",
    "created_at": "2026-10-03T12:00:00Z",
    "updated_at": "2026-10-03T12:00:00Z"
  }
]
```

#### `GET /books/{book_id}`
Fetch detailed information for a single book.

**Response (`200 OK`):**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "description": "A Handbook of Agile Software Craftsmanship",
  "category": "Technology",
  "status": "AVAILABLE",
  "created_at": "2026-10-03T12:00:00Z",
  "updated_at": "2026-10-03T12:00:00Z"
}
```

---

### 3. Online Book Borrowing (User Route)

#### `POST /books/{book_id}/borrow`
Borrow a book online. Automatically updates book status to `BORROWED` and returns a pick-up token.

**Request Body:**
```json
{
  "user_name": "John Doe",
  "user_email": "john.doe@example.com",
  "user_phone": "+1-555-0199",
  "user_address": "123 Main Street, Suite 400"
}
```

**Response (`201 Created`):**
```json
{
  "token": "LIB-9X82-K4M1",
  "status": "PENDING_PICKUP",
  "book_id": 1,
  "book_title": "Clean Code",
  "user_name": "John Doe",
  "user_email": "john.doe@example.com",
  "user_phone": "+1-555-0199",
  "user_address": "123 Main Street, Suite 400",
  "borrowed_at": "2026-10-03T13:45:00Z",
  "instructions": "Please present this token at the physical library front desk to pick up your book."
}
```

#### `GET /borrow/verify/{token}`
Public or staff verification of a pick-up token.

**Response (`200 OK`):**
```json
{
  "valid": true,
  "token": "LIB-9X82-K4M1",
  "status": "PENDING_PICKUP",
  "book": {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "description": "A Handbook of Agile Software Craftsmanship",
    "category": "Technology",
    "status": "BORROWED",
    "created_at": "2026-10-03T12:00:00Z",
    "updated_at": "2026-10-03T13:45:00Z"
  },
  "borrower_name": "John Doe",
  "borrower_email": "john.doe@example.com",
  "borrowed_at": "2026-10-03T13:45:00Z",
  "fulfilled_at": null,
  "returned_at": null
}
```

---

### 4. Admin Management Endpoints (Requires `Authorization: Bearer <token>`)

#### `POST /admin/books`
Create a new book in the library catalog.

**Request Body:**
```json
{
  "title": "Design Patterns",
  "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
  "isbn": "978-0201633610",
  "description": "Elements of Reusable Object-Oriented Software",
  "category": "Computer Science"
}
```

#### `PUT /admin/books/{book_id}`
Update details of an existing book.

#### `PATCH /admin/books/{book_id}/status`
Manually change book status (`AVAILABLE`, `BORROWED`, `MAINTENANCE`, `RESERVED`).

**Request Body:**
```json
{
  "status": "MAINTENANCE"
}
```

#### `DELETE /admin/books/{book_id}`
Delete a book from the system (`204 No Content`).

#### `GET /admin/borrowing-history`
View all borrowing records with filters (`status`, `token`, `user_email`, `book_id`).

#### `PATCH /admin/borrowing-history/{record_id}/fulfill`
Mark physical book pickup as completed. Sets `status` to `FULFILLED` and updates `fulfilled_at`.

#### `PATCH /admin/borrowing-history/{record_id}/return`
Process book return. Sets record status to `RETURNED`, records `returned_at`, and automatically resets the book status back to `AVAILABLE`.

---

## 🤖 Guidance for Next.js AI Agent / Frontend Engineer

If you are prompting another AI to generate the **Next.js Frontend**:

1. **API Base URL**: Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`.
2. **Public Pages**:
   - `/books` - Grid/List view with search input & category filter pills.
   - `/books/[id]` - Book detail page with a "Borrow Book" modal form requesting user `name`, `email`, `phone`, `address`.
   - `/borrow/success` - Receipt screen showing the generated `LIB-XXXX-XXXX` token and QR code / barcode.
   - `/verify` - Token verification lookup tool.
3. **Admin Dashboard**:
   - `/admin/login` - Simple login form storing JWT token in `localStorage` or HTTP cookie.
   - `/admin/books` - CRUD table with add/edit modals and quick status change toggles.
   - `/admin/history` - History log table with "Fulfill Pickup" and "Process Return" action buttons.
