from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.lower().strip()))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def login(db: Session, email: str, password: str) -> str:
    user = authenticate(db, email, password)
    if not user:
        raise ValueError("Incorrect email or password")
    return create_access_token(str(user.id), user.role.value)
