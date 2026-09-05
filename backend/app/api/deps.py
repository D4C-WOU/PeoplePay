import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:

    credentials_error = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        subject = payload.get("sub")
        token_role = payload.get("role")

        if not subject or not token_role:
            raise credentials_error

    except (
        jwt.InvalidTokenError,
        TypeError,
        ValueError,
    ):
        raise credentials_error

    user = db.get(User, subject)

    if user is None:
        raise credentials_error

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    if user.role.value != token_role:
        raise HTTPException(
            status_code=401,
            detail="Authentication role is no longer valid",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    return user
