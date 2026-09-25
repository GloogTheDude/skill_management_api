from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from dto.employee_diploma_dto import (
    CreateEmployeeDiplomaDTO,
    ResponseEmployeeDiplomaDTO,
    UpdateEmployeeDiplomaDTO,
)
from services.employee_diploma_service import EmployeeDiplomaService


router = APIRouter(
    prefix="/employee_diploma",
    tags=["employee_diploma"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee_diploma(
    dto: CreateEmployeeDiplomaDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.create(dto)


@router.get("/{id_employee}/{id_diploma}")
def get_employee_diploma_by_ids(
    id_employee: int,
    id_diploma: int,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.get_by_id(id_employee, id_diploma)


@router.get("")
def get_employee_diplomas(
    session: Session = Depends(get_session),
) -> list[ResponseEmployeeDiplomaDTO]:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.get_all()


@router.patch("/{id_employee}/{id_diploma}")
def update_employee_diploma(
    id_employee: int,
    id_diploma: int,
    dto: UpdateEmployeeDiplomaDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.update(id_employee, id_diploma, dto)


@router.delete("/{id_employee}/{id_diploma}")
def delete_employee_diploma(
    id_employee: int,
    id_diploma: int,
    session: Session = Depends(get_session),
):
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.delete((id_employee, id_diploma))
