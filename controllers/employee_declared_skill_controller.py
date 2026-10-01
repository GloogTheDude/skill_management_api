from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from controllers.auth_controller import get_current_employee, require_hr_employee
from core.database import get_session
from db.repositories.employee_declared_skill_repository import EmployeeDeclaredSkillRepository
from dto.auth_dto import AuthEmployeeDTO
from dto.employee_declared_skill_dto import CreateEmployeeDeclaredSkillDTO, ResponseEmployeeDeclaredSkillDTO, UpdateEmployeeDeclaredSkillDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from services.employee_authorization_service import EmployeeAuthorizationService
from services.employee_declared_skill_service import EmployeeDeclaredSkillService

router = APIRouter(prefix="/employee_declared_skill", tags=["employee_declared_skill"])


def service(session):
    return EmployeeDeclaredSkillService(EmployeeDeclaredSkillRepository(session))


@router.post("", status_code=status.HTTP_201_CREATED)
def create(dto: CreateEmployeeDeclaredSkillDTO, session: Session = Depends(get_session), _: AuthEmployeeDTO = Depends(require_hr_employee)) -> ResponseEmployeeDeclaredSkillDTO:
    try:
        return service(session).create(dto)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Employee or Skill not found") from exc


@router.get("/employee/{id_employee}")
def get_for_employee(id_employee: int, session: Session = Depends(get_session), current: AuthEmployeeDTO = Depends(get_current_employee)) -> list[ResponseEmployeeDeclaredSkillDTO]:
    employee = session.get(Employee, id_employee)
    if employee is None or employee.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current, employee)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return service(session).get_for_employee(id_employee)


@router.patch("/{id_employee_declared_skill}")
def update(id_employee_declared_skill: int, dto: UpdateEmployeeDeclaredSkillDTO, session: Session = Depends(get_session), _: AuthEmployeeDTO = Depends(require_hr_employee)) -> ResponseEmployeeDeclaredSkillDTO:
    return service(session).update(id_employee_declared_skill, dto)


@router.delete("/{id_employee_declared_skill}")
def archive(id_employee_declared_skill: int, session: Session = Depends(get_session), _: AuthEmployeeDTO = Depends(require_hr_employee)) -> ResponseEmployeeDeclaredSkillDTO:
    return service(session).archive(id_employee_declared_skill)
