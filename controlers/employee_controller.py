from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_repository import EmployeeRepository
from dto.employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
    ResponseEmployeeDTO,
)
from services.employee_service import EmployeeService


router = APIRouter(
    prefix="/employee",
    tags=["employee"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee(
    dto: CreateEmployeeDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    return service.create(dto)


@router.get("/{id_employee}")
def get_employee_by_id(
    id_employee: int,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    return service.get_by_id(id_employee)


@router.get("")
def get_employees(
    session: Session = Depends(get_session),
) -> list[ResponseEmployeeDTO]:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    return service.get_all()


@router.patch("/{id_employee}")
def update_employee(
    id_employee: int,
    dto: UpdateEmployeeDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    return service.update(id_employee, dto)


@router.delete("/{id_employee}")
def delete_employee(
    id_employee: int,
    session: Session = Depends(get_session),
):
    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    return service.delete(id_employee)