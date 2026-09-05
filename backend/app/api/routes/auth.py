from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import login

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_route(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        token = login(
            db,
            str(data.email),
            data.password,
        )

        return TokenResponse(
            access_token=token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user: User = Depends(get_current_active_user),
):
    return user
