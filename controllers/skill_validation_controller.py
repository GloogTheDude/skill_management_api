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
from controllers.auth_controller import get_current_employee, require_hr_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from models.skill import Skill
from models.validation_type import ValidationType
from services.employee_authorization_service import EmployeeAuthorizationService
from dto.skill_evaluation_queue_dto import BatchSkillEvaluationDTO


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
    skill = session.get(Skill, dto.id_skill)
    if skill is None or skill.is_deleted:
        raise HTTPException(status_code=404, detail="Skill not found")
    validation_type = session.get(ValidationType, dto.id_validation)
    if validation_type is None or validation_type.is_deleted:
        raise HTTPException(status_code=404, detail="Validation type not found")
    try:
        if current_employee.id_employee == dto.id_employee:
            raise AuthorizationForbidden("Employees cannot validate themselves.")
        EmployeeAuthorizationService.authorize_action(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return service.create(dto, current_employee.id_employee)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def create_skill_validation_batch(
    dto: BatchSkillEvaluationDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    target = session.get(Employee, dto.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        if current_employee.id_employee == dto.id_employee:
            raise AuthorizationForbidden("Employees cannot validate themselves.")
        EmployeeAuthorizationService.authorize_action(current_employee, target)
        return SkillValidationService(SkillValidationRepository(session)).create_batch(
            dto, current_employee.id_employee
        )
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Validation reference not found") from exc


@router.get("/work-queue/history")
def get_evaluation_history_queue(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        EmployeeAuthorizationService.require_manager_or_hr(current_employee)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return SkillValidationService(SkillValidationRepository(session)).get_evaluation_history(
        current_employee.id_employee, current_employee.permission_profile
    )


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
    return service.get_all(current_employee.id_employee, current_employee.permission_profile)


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


@router.get("/employees/{id_employee}/skills/{id_skill}/history")
def get_skill_validation_history(
    id_employee: int,
    id_skill: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    target = session.get(Employee, id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return SkillValidationService(SkillValidationRepository(session)).get_history(id_employee, id_skill)


@router.delete("/{id_skill_validation}")
def delete_skill_validation(
    id_skill_validation: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
):
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.delete(id_skill_validation)
