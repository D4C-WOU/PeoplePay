from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_route(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return TokenResponse(access_token=login(db, str(data.email), data.password))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc),
                            headers={"WWW-Authenticate": "Bearer"})


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_active_user)):
    return user
