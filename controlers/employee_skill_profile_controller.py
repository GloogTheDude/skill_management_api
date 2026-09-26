from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.skill_dto import SkillProfileDTO
from services.employee_skill_profile_service import EmployeeSkillProfileService


router = APIRouter(tags=["employee skills"])


@router.get(
    "/employees/{id_employee}/skills",
    response_model=list[SkillProfileDTO],
)
def get_employee_skill_profile(
    id_employee: int,
    session: Session = Depends(get_session),
) -> list[SkillProfileDTO]:
    service = EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    )
    return service.get_profile(id_employee)
