import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Create in-memory SQLite database for automated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def get_admin_token():
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "admin", "password": "adminsecret"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_auth():
    # Test invalid credentials
    res = client.post(
        "/api/v1/auth/login/json",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert res.status_code == 401

    # Test valid credentials
    res = client.post(
        "/api/v1/auth/login/json",
        json={"username": "admin", "password": "adminsecret"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_book_crud_and_borrow_flow():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Admin creates a book
    book_payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "description": "A Handbook of Agile Software Craftsmanship",
        "category": "Software",
    }
    create_res = client.post("/api/v1/admin/books", json=book_payload, headers=headers)
    assert create_res.status_code == 201
    book = create_res.json()
    book_id = book["id"]
    assert book["status"] == "AVAILABLE"

    # 2. Public lists books
    list_res = client.get("/api/v1/books")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Public gets single book
    get_res = client.get(f"/api/v1/books/{book_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Clean Code"

    # 4. User borrows the book
    borrow_payload = {
        "user_name": "Alice Johnson",
        "user_email": "alice@example.com",
        "user_phone": "+1-555-0100",
        "user_address": "456 Tech Ave",
    }
    borrow_res = client.post(f"/api/v1/books/{book_id}/borrow", json=borrow_payload)
    assert borrow_res.status_code == 201
    borrow_data = borrow_res.json()
    pickup_token = borrow_data["token"]
    assert pickup_token.startswith("LIB-")
    assert borrow_data["status"] == "PENDING_PICKUP"

    # 5. Check book status is now BORROWED
    get_res_after = client.get(f"/api/v1/books/{book_id}")
    assert get_res_after.json()["status"] == "BORROWED"

    # 6. Attempting to borrow again should fail
    borrow_fail = client.post(f"/api/v1/books/{book_id}/borrow", json=borrow_payload)
    assert borrow_fail.status_code == 400

    # 7. Verify token public endpoint
    verify_res = client.get(f"/api/v1/borrow/verify/{pickup_token}")
    assert verify_res.status_code == 200
    assert verify_res.json()["valid"] is True
    assert verify_res.json()["borrower_name"] == "Alice Johnson"

    # 8. Admin views borrowing history
    history_res = client.get("/api/v1/admin/borrowing-history", headers=headers)
    assert history_res.status_code == 200
    records = history_res.json()
    assert len(records) == 1
    record_id = records[0]["id"]

    # 9. Admin fulfills pickup
    fulfill_res = client.patch(
        f"/api/v1/admin/borrowing-history/{record_id}/fulfill", headers=headers
    )
    assert fulfill_res.status_code == 200
    assert fulfill_res.json()["status"] == "FULFILLED"

    # 10. Admin processes return
    return_res = client.patch(
        f"/api/v1/admin/borrowing-history/{record_id}/return", headers=headers
    )
    assert return_res.status_code == 200
    assert return_res.json()["status"] == "RETURNED"

    # 11. Book status should be back to AVAILABLE
    get_res_final = client.get(f"/api/v1/books/{book_id}")
    assert get_res_final.json()["status"] == "AVAILABLE"
