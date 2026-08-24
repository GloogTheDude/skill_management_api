
from db.repositories.search_employee_skills_repository import SearchEmployeeSkillRepository
from dto.search_employee_dto import SearchEmployeeDTO


class SearchEmployeeSkillsService:
    def __init__(self, repo_employee_skill:SearchEmployeeSkillRepository):
        self.repo_employee_skill = repo_employee_skill 
    
    def fetch_employee_skills(self) -> dict[int, SearchEmployeeDTO]:
        employees = {}
        result = self.repo_employee_skill.fetch_skills_employee()

        for row in result:
            id_employee = row.id_employee
            id_skill = row.id_skill

            if id_employee not in employees:
                employees[id_employee] = SearchEmployeeDTO(
                    id_employee=row.id_employee,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    skills={},
                )

            employees[id_employee].skills[id_skill] = [
                row.name_skill,
                row.max_level,
            ]

        return employees