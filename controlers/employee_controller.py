from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_repository import EmployeeRepository
from dto.employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
    ResponseEmployeeDTO,
)
from services.employee_service import EmployeeService
from controlers.auth_controller import get_current_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import TrainingRequestForbidden
from services.employee_authorization_service import EmployeeAuthorizationService
from sqlalchemy.exc import NoResultFound


router = APIRouter(
    prefix="/employee",
    tags=["employee"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee(
    dto: CreateEmployeeDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    try:
        EmployeeAuthorizationService.require_hr(current_employee)
        return service.create(dto)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/{id_employee}")
def get_employee_by_id(
    id_employee: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    try:
        return service.get_by_id(id_employee, current_employee)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Employee not found.") from exc
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("")
def get_employees(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ResponseEmployeeDTO]:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    try:
        EmployeeAuthorizationService.require_hr(current_employee)
        return service.get_all()
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.patch("/{id_employee}")
def update_employee(
    id_employee: int,
    dto: UpdateEmployeeDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseEmployeeDTO:

    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    try:
        EmployeeAuthorizationService.require_hr(current_employee)
        return service.update(id_employee, dto)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.delete("/{id_employee}")
def delete_employee(
    id_employee: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    repo = EmployeeRepository(session)
    service = EmployeeService(repo)

    try:
        EmployeeAuthorizationService.require_hr(current_employee)
        return service.delete(id_employee)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
