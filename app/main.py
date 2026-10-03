from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import admin, auth, books, borrow


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: handles startup and shutdown tasks."""
    # Ensure database tables are created on startup
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 📚 FastAPI Library Backend API

A clean RESTful API for library management built with FastAPI, PostgreSQL, and SQLAlchemy.

### Features
* 🔐 **Admin Authentication**: Environment variable credentials with JWT bearer auth.
* 📖 **Book Management**: Full CRUD operations & manual status updates for admins.
* 🏷️ **User Online Borrowing**: Instant book status updates & unique pick-up token generation.
* 🎫 **Token Verification**: Verify pick-up tokens for physical library fulfillment.
* 📋 **Borrowing History & Returns**: Track borrowing records and process book returns.

### Documentation & Client Integration
* **Interactive Swagger UI**: [/docs](/docs)
* **ReDoc OpenAPI Documentation**: [/redoc](/redoc)
""",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Next.js and frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production as required
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrow.router)
app.include_router(admin.router)


@app.get("/", tags=["Health Check"])
def root():
    """Root status endpoint."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    """System health check endpoint."""
    return {"status": "healthy"}
