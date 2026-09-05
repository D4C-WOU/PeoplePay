import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole


def seed(db: Session) -> None:
    password = os.getenv("SEED_PASSWORD")
    if not password:
        raise RuntimeError("SEED_PASSWORD must be set for development seeding")
    defaults = [
        ("admin@example.local", UserRole.ADMIN),
        ("hr@example.local", UserRole.HR),
        ("manager@example.local", UserRole.MANAGER),
    ]
    for email, role in defaults:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(email=email, role=role, password_hash=hash_password(password), is_active=True))
    db.commit()


if __name__ == "__main__":
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
