from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from dto.employee_diploma_dto import (
    CreateEmployeeDiplomaDTO,
    ResponseEmployeeDiplomaDTO,
    UpdateEmployeeDiplomaDTO,
)
from services.employee_diploma_service import EmployeeDiplomaService
from controllers.auth_controller import get_current_employee, require_hr_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from services.employee_authorization_service import EmployeeAuthorizationService


router = APIRouter(
    prefix="/employee_diploma",
    tags=["employee_diploma"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee_diploma(
    dto: CreateEmployeeDiplomaDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.create(dto)


@router.get("/{id_employee}/{id_diploma}")
def get_employee_diploma_by_ids(
    id_employee: int,
    id_diploma: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    result = service.get_by_id(id_employee, id_diploma)
    target = session.get(Employee, result.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return result


@router.get("")
def get_employee_diplomas(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ResponseEmployeeDiplomaDTO]:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.get_all(current_employee.id_employee, current_employee.permission_profile)


@router.patch("/{id_employee}/{id_diploma}")
def update_employee_diploma(
    id_employee: int,
    id_diploma: int,
    dto: UpdateEmployeeDiplomaDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseEmployeeDiplomaDTO:
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.update(id_employee, id_diploma, dto)


@router.delete("/{id_employee}/{id_diploma}")
def delete_employee_diploma(
    id_employee: int,
    id_diploma: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
):
    repo = EmployeeDiplomaRepository(session)
    service = EmployeeDiplomaService(repo)
    return service.delete((id_employee, id_diploma))
