from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission, require_roles
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class UserUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    role: UserRole | None = None
    is_active: bool | None = None


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "users:read",
    )

    return list(db.scalars(select(User).order_by(User.email)).all())


@router.get(
    "/{id}",
    response_model=UserResponse,
)
def get_user(
    id: str,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "users:read",
    )

    obj = db.get(
        User,
        id,
    )

    if obj is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return obj


@router.patch(
    "/{id}",
    response_model=UserResponse,
)
def update_user(
    id: str,
    data: UserUpdate,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_roles(
        user,
        UserRole.ADMIN,
    )

    obj = db.get(
        User,
        id,
    )

    if obj is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    updates = data.model_dump(
        exclude_unset=True,
    )

    if obj.id == user.id and updates.get("is_active") is False:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account",
        )

    for field, value in updates.items():
        setattr(
            obj,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(obj)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="User could not be updated",
        )

    return obj
