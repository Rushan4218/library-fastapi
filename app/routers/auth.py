from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, verify_admin_credentials
from app.config import settings
from app.schemas import AdminLogin, Token

router = APIRouter(prefix="/api/v1/auth", tags=["Admin Authentication"])


@router.post("/login", response_model=Token, summary="Admin Login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate Admin using credentials defined in environment variables.
    
    Supports form submission (Swagger UI friendly).
    """
    if not verify_admin_credentials(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": settings.ADMIN_USERNAME}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token, summary="Admin Login (JSON format)")
def login_json(credentials: AdminLogin):
    """Authenticate Admin using JSON request body.
    
    Ideal for Next.js frontend applications sending JSON.
    """
    if not verify_admin_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": settings.ADMIN_USERNAME}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
