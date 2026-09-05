from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.salary_rule import SalaryRule
from app.models.salary_structure import SalaryStructure
from app.schemas.salary_rule import SalaryRuleCreate,SalaryRuleResponse,SalaryRuleUpdate
from app.services.validation_service import validate_salary_rule

router=APIRouter(prefix="/salary/rules",tags=["Salary"])
@router.get("",response_model=list[SalaryRuleResponse])
def list_(structure_id:str|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:read");stmt=select(SalaryRule).order_by(SalaryRule.sequence)
    if structure_id:stmt=stmt.where(SalaryRule.salary_structure_id==structure_id)
    return db.scalars(stmt).all()
@router.post("",response_model=SalaryRuleResponse,status_code=201)
def create(data:SalaryRuleCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:write")
    if not db.get(SalaryStructure,data.salary_structure_id):raise HTTPException(404,"Salary structure not found")
    obj=SalaryRule(**data.model_dump());validate_salary_rule(obj)
    if db.scalar(select(SalaryRule).where(SalaryRule.salary_structure_id==obj.salary_structure_id,SalaryRule.code==obj.code)):raise HTTPException(409,"Rule code already exists")
    db.add(obj);db.commit();db.refresh(obj);return obj
@router.get("/{id}",response_model=SalaryRuleResponse)
def get(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:read");obj=db.get(SalaryRule,id)
    if not obj:raise HTTPException(404,"Salary rule not found")
    return obj
@router.patch("/{id}",response_model=SalaryRuleResponse)
def update(id:str,data:SalaryRuleUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"salary:write");obj=db.get(SalaryRule,id)
    if not obj:raise HTTPException(404,"Salary rule not found")
    for k,v in data.model_dump(exclude_unset=True).items():setattr(obj,k,v)
    try:validate_salary_rule(obj)
    except ValueError as exc:raise HTTPException(422,str(exc))
    db.commit();db.refresh(obj);return obj
