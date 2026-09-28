from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.skill_dto import SkillProfileDTO
from services.employee_skill_profile_service import EmployeeSkillProfileService
from controllers.auth_controller import get_current_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from sqlalchemy.exc import NoResultFound


router = APIRouter(tags=["employee skills"])


@router.get(
    "/employees/{id_employee}/skills",
    response_model=list[SkillProfileDTO],
)
def get_employee_skill_profile(
    id_employee: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[SkillProfileDTO]:
    service = EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    )
    try:
        return service.get_profile(id_employee, current_employee)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Employee not found.") from exc
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
