from fastapi import APIRouter, Depends, HTTPException
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
from controlers.auth_controller import get_current_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden


router = APIRouter(tags=["employee skills"])


@router.post(
    "/employees/search-by-skills",
    response_model=list[EmployeeSkillSearchResultDTO],
)
def search_employees_by_skills(
    dto: EmployeeSkillSearchRequestDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[EmployeeSkillSearchResultDTO]:
    service = EmployeeSkillSearchService(EmployeeSkillSearchRepository(session))
    try:
        return service.search(dto, current_employee)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
