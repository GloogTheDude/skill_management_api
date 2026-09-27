from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from dto.employee_certification_crud_dto import (
    CreateEmployeeCertificationDTO,
    ResponseEmployeeCertificationDTO,
    UpdateEmployeeCertificationDTO,
)
from services.employee_certification_service import EmployeeCertificationService
from controlers.auth_controller import get_current_employee, require_hr_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import TrainingRequestForbidden
from models.employee import Employee
from services.training_request_authorization import TrainingRequestAuthorization


router = APIRouter(
    prefix="/employee_certification",
    tags=["employee_certification"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee_certification(
    dto: CreateEmployeeCertificationDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.create(dto)


@router.get("/{id_employee_certification}")
def get_employee_certification_by_id(
    id_employee_certification: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    result = service.get_by_id(id_employee_certification)
    target = session.get(Employee, result.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(current_employee, target)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return result


@router.get("")
def get_employee_certifications(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ResponseEmployeeCertificationDTO]:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.get_all(current_employee.id_employee, current_employee.access_level)


@router.patch("/{id_employee_certification}")
def update_employee_certification(
    id_employee_certification: int,
    dto: UpdateEmployeeCertificationDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.update(id_employee_certification, dto)


@router.delete("/{id_employee_certification}")
def delete_employee_certification(
    id_employee_certification: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
):
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.delete(id_employee_certification)
