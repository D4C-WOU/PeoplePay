from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractStatus
from app.models.employee import Employee, EmployeeStatus
from app.models.salary_structure import SalaryStructure
from app.models.work_schedule import WorkSchedule


def get_contract(
    db: Session,
    contract_id: str,
) -> Contract:
    contract = db.get(Contract, contract_id)

    if contract is None:
        raise ValueError("Contract not found")

    return contract


def list_contracts(
    db: Session,
    employee_id: str | None = None,
    status: ContractStatus | None = None,
) -> list[Contract]:
    stmt = select(Contract)

    if employee_id is not None:
        stmt = stmt.where(
            Contract.employee_id == employee_id
        )

    if status is not None:
        stmt = stmt.where(
            Contract.status == status
        )

    stmt = stmt.order_by(
        Contract.start_date.desc()
    )

    return list(db.scalars(stmt).all())


def _validate_dependencies(
    db: Session,
    employee_id: str,
    salary_structure_id: str,
    work_schedule_id: str | None,
) -> Employee:
    employee = db.get(Employee, employee_id)

    if employee is None:
        raise ValueError("Employee not found")

    if employee.status == EmployeeStatus.TERMINATED:
        raise ValueError(
            "A terminated employee cannot have a new contract"
        )

    salary_structure = db.get(
        SalaryStructure,
        salary_structure_id,
    )

    if salary_structure is None:
        raise ValueError(
            "Salary structure not found"
        )

    if not salary_structure.is_active:
        raise ValueError(
            "Salary structure is inactive"
        )

    if work_schedule_id is not None:
        work_schedule = db.get(
            WorkSchedule,
            work_schedule_id,
        )

        if work_schedule is None:
            raise ValueError(
                "Work schedule not found"
            )

        if not work_schedule.is_active:
            raise ValueError(
                "Work schedule is inactive"
            )

    return employee


def _check_contract_overlap(
    db: Session,
    employee_id: str,
    start_date: date,
    end_date: date | None,
    exclude_contract_id: str | None = None,
) -> None:
    """
    Prevent overlapping ACTIVE contracts for the same employee.

    A None end_date means the contract is open-ended.
    """

    stmt = select(Contract).where(
        Contract.employee_id == employee_id,
        Contract.status == ContractStatus.ACTIVE,
    )

    if exclude_contract_id is not None:
        stmt = stmt.where(
            Contract.id != exclude_contract_id
        )

    existing_contracts = list(
        db.scalars(stmt).all()
    )

    for existing in existing_contracts:

        # Existing contract has no end date.
        if existing.end_date is None:
            raise ValueError(
                "Employee already has an overlapping active contract"
            )

        # New contract has no end date.
        if end_date is None:
            if start_date <= existing.end_date:
                raise ValueError(
                    "Employee already has an overlapping active contract"
                )

            continue

        # Both contracts have end dates.
        if (
            start_date <= existing.end_date
            and end_date >= existing.start_date
        ):
            raise ValueError(
                "Employee already has an overlapping active contract"
            )


def create_contract(
    db: Session,
    data: dict,
) -> Contract:
    employee_id = data["employee_id"]
    salary_structure_id = data["salary_structure_id"]
    work_schedule_id = data.get("work_schedule_id")

    start_date = data["start_date"]
    end_date = data.get("end_date")

    status = data.get(
        "status",
        ContractStatus.ACTIVE,
    )

    # ---------------------------------------------------------
    # Date validation
    # ---------------------------------------------------------

    if (
        end_date is not None
        and end_date < start_date
    ):
        raise ValueError(
            "End date cannot be before start date"
        )

    # ---------------------------------------------------------
    # Dependency validation
    # ---------------------------------------------------------

    _validate_dependencies(
        db=db,
        employee_id=employee_id,
        salary_structure_id=salary_structure_id,
        work_schedule_id=work_schedule_id,
    )

    # ---------------------------------------------------------
    # Active contract overlap validation
    # ---------------------------------------------------------

    if status == ContractStatus.ACTIVE:
        _check_contract_overlap(
            db=db,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
        )

    # ---------------------------------------------------------
    # Create contract
    # ---------------------------------------------------------

    contract = Contract(**data)

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Contract could not be created. "
            "The contract number may already exist."
        )

    return contract


def update_contract(
    db: Session,
    contract: Contract,
    updates: dict,
) -> Contract:
    new_end_date = updates.get(
        "end_date",
        contract.end_date,
    )

    # ---------------------------------------------------------
    # Date validation
    # ---------------------------------------------------------

    if (
        new_end_date is not None
        and new_end_date < contract.start_date
    ):
        raise ValueError(
            "End date cannot be before start date"
        )

    # ---------------------------------------------------------
    # Active contract overlap validation
    # ---------------------------------------------------------

    if contract.status == ContractStatus.ACTIVE:
        _check_contract_overlap(
            db=db,
            employee_id=contract.employee_id,
            start_date=contract.start_date,
            end_date=new_end_date,
            exclude_contract_id=contract.id,
        )

    # ---------------------------------------------------------
    # Apply updates
    # ---------------------------------------------------------

    allowed_fields = {
        "end_date",
        "contract_type",
        "base_salary",
        "currency",
        "notes",
    }

    for field, value in updates.items():
        if field in allowed_fields:
            setattr(
                contract,
                field,
                value,
            )

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Contract could not be updated"
        )

    return contract


def terminate_contract(
    db: Session,
    contract: Contract,
) -> Contract:
    if contract.status == ContractStatus.TERMINATED:
        return contract

    contract.status = ContractStatus.TERMINATED

    if contract.end_date is None:
        contract.end_date = date.today()

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Contract could not be terminated"
        )

    return contract