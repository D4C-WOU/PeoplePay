from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.salary_structure import SalaryStructure
from app.schemas.salary_structure import SalaryStructureCreate,SalaryStructureResponse,SalaryStructureUpdate

router=APIRouter(prefix="/salary/structures",tags=["Salary"])
@router.get("",response_model=list[SalaryStructureResponse])
def list_(user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:read");return db.scalars(select(SalaryStructure).order_by(SalaryStructure.name)).all()
@router.post("",response_model=SalaryStructureResponse,status_code=201)
def create(data:SalaryStructureCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:write")
    if db.scalar(select(SalaryStructure).where(SalaryStructure.code==data.code)):raise HTTPException(409,"Structure code already exists")
    obj=SalaryStructure(**data.model_dump());db.add(obj);db.commit();db.refresh(obj);return obj
@router.get("/{id}",response_model=SalaryStructureResponse)
def get(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:read");obj=db.get(SalaryStructure,id)
    if not obj:raise HTTPException(404,"Salary structure not found")
    return obj
@router.patch("/{id}",response_model=SalaryStructureResponse)
def update(id:str,data:SalaryStructureUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:write");obj=db.get(SalaryStructure,id)
    if not obj:raise HTTPException(404,"Salary structure not found")
    for k,v in data.model_dump(exclude_unset=True).items():setattr(obj,k,v)
    db.commit();db.refresh(obj);return obj
