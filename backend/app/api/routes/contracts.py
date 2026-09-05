from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.contract import ContractStatus
from app.schemas.contract import ContractCreate, ContractResponse, ContractUpdate
from app.services import contract_service

router=APIRouter(prefix="/contracts",tags=["Contracts"])

@router.get("",response_model=list[ContractResponse])
def list_contracts(employee_id:str|None=None,status:ContractStatus|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"contracts:read"); return contract_service.list_contracts(db,employee_id,status)

@router.post("",response_model=ContractResponse,status_code=201)
def create(data:ContractCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"contracts:write")
    try:return contract_service.create_contract(db,data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))

@router.get("/{contract_id}",response_model=ContractResponse)
def get(contract_id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"contracts:read")
    try:return contract_service.get_contract(db,contract_id)
    except ValueError as exc:raise HTTPException(404,str(exc))

@router.patch("/{contract_id}",response_model=ContractResponse)
def update(contract_id:str,data:ContractUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"contracts:write")
    try:return contract_service.update_contract(db,contract_service.get_contract(db,contract_id),data.model_dump(exclude_unset=True))
    except ValueError as exc:raise HTTPException(409,str(exc))
