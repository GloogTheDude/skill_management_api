from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_skill_search_repository import (
    EmployeeSkillSearchRepository,
)
from dto.employee_skill_search_dto import (
    EmployeeSkillSearchRequestDTO,
    EmployeeSkillSearchResultDTO,
)
from services.employee_skill_search_service import EmployeeSkillSearchService


router = APIRouter(tags=["employee skills"])


@router.post(
    "/employees/search-by-skills",
    response_model=list[EmployeeSkillSearchResultDTO],
)
def search_employees_by_skills(
    dto: EmployeeSkillSearchRequestDTO,
    session: Session = Depends(get_session),
) -> list[EmployeeSkillSearchResultDTO]:
    service = EmployeeSkillSearchService(EmployeeSkillSearchRepository(session))
    return service.search(dto)
