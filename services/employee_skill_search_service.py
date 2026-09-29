from dto.employee_skill_search_dto import (
    EmployeeSkillSearchRequestDTO,
    EmployeeSkillSearchResultDTO,
)
from dto.skill_dto import SkillSourceDTO
from db.repositories.employee_skill_search_repository import (
    EmployeeSkillSearchRepository,
)
from services.skill_profile_aggregation import add_skill_source, finalize_skill_dimensions
from dto.auth_dto import AuthEmployeeDTO
from services.employee_authorization_service import EmployeeAuthorizationService


class EmployeeSkillSearchService:
    def __init__(self, repository: EmployeeSkillSearchRepository):
        self.repository = repository

    def search(
        self,
        dto: EmployeeSkillSearchRequestDTO,
        current_employee: AuthEmployeeDTO | None = None,
    ) -> list[EmployeeSkillSearchResultDTO]:
        manager_id = None
        if current_employee is not None:
            EmployeeAuthorizationService.require_manager_or_hr(current_employee)
            from core.constants import PermissionProfile
            if current_employee.permission_profile == PermissionProfile.MANAGER:
                manager_id = current_employee.id_employee
        rows = self.repository.search(dto.requirements, manager_id=manager_id)
        employees = {}

        for row in rows:
            employee = employees.setdefault(
                row.id_employee,
                {
                    "id_employee": row.id_employee,
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    "profiles": {},
                },
            )
            add_skill_source(
                employee["profiles"],
                skill_id=row.id_skill,
                skill_name=row.skill_name,
                skill_domaine=row.skill_domaine,
                source=SkillSourceDTO(
                    source_type=row.source_type,
                    source_id=row.source_id,
                    level=row.level,
                    is_active=bool(row.is_active),
                    acquired_at=row.acquired_at,
                    expires_at=row.expires_at,
                ),
            )

        for employee in employees.values():
            for profile in employee["profiles"].values():
                finalize_skill_dimensions(profile)

        return [
            EmployeeSkillSearchResultDTO(
                id_employee=employee["id_employee"],
                first_name=employee["first_name"],
                last_name=employee["last_name"],
                skills=list(employee["profiles"].values()),
            )
            for employee in employees.values()
        ]
