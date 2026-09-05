from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


def authenticate(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    normalized_email = email.lower().strip()

    user = db.scalar(select(User).where(User.email == normalized_email))

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def login(
    db: Session,
    email: str,
    password: str,
) -> str:

    user = authenticate(
        db,
        email,
        password,
    )

    if user is None:
        raise ValueError("Incorrect email or password")

    return create_access_token(
        str(user.id),
        user.role.value,
    )
