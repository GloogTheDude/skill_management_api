from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.skill_validation_repository import SkillValidationRepository
from dto.skill_validation_dto import (
    CreateSkillValidationDTO,
    UpdateSkillValidationDTO,
    ResponseSkillValidationDTO,
)
from services.skill_validation_service import SkillValidationService
from controlers.auth_controller import get_current_employee, require_hr_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from services.employee_authorization_service import EmployeeAuthorizationService


router = APIRouter(
    prefix="/skill_validation",
    tags=["skill_validation"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_skill_validation(
    dto: CreateSkillValidationDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    target = session.get(Employee, dto.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.authorize_action(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return service.create(dto, current_employee.id_employee)


@router.get("/{id_skill_validation}")
def get_skill_validation_by_id(
    id_skill_validation: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    result = service.get_by_id(id_skill_validation)
    target = session.get(Employee, result.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return result


@router.get("")
def get_skill_validations(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ResponseSkillValidationDTO]:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.get_all(current_employee.id_employee, current_employee.access_level)


@router.patch("/{id_skill_validation}")
def update_skill_validation(
    id_skill_validation: int,
    dto: UpdateSkillValidationDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.update(id_skill_validation, dto)


@router.delete("/{id_skill_validation}")
def delete_skill_validation(
    id_skill_validation: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
):
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.delete(id_skill_validation)
