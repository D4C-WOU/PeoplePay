from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission, require_roles
from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User,UserRole
from app.schemas.auth import UserResponse

router=APIRouter(prefix="/users",tags=["Users"])
class UserUpdate(BaseModel):
    role: UserRole|None=None
    is_active: bool|None=None
@router.get("",response_model=list[UserResponse])
def list_(user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"users:read");return db.scalars(select(User).order_by(User.email)).all()
@router.get("/{id}",response_model=UserResponse)
def get(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"users:read");obj=db.get(User,id)
    if not obj:raise HTTPException(404,"User not found")
    return obj
@router.patch("/{id}",response_model=UserResponse)
def update(id:str,data:UserUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_roles(user,UserRole.ADMIN)
    obj=db.get(User,id)
    if not obj:raise HTTPException(404,"User not found")
    for k,v in data.model_dump(exclude_unset=True).items():setattr(obj,k,v)
    db.commit();db.refresh(obj);return obj
