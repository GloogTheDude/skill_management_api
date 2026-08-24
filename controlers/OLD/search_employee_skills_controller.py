
from core.database import SessionLocal
from db.repositories.search_employee_skills_repository import SearchEmployeeSkillRepository
from db.repositories.skills_repository import SkillRepository
from services.search_employee_skills_service import SearchEmployeeSkillsService
from menus.search_employee_skills_menu import SearchEmployeeSkillsMenu as sesm
from services.skill_service import SkillService


class SearchEmployeeSkillsController:
    def __init__(self):
        self.requisite = []
        self.employees = {}
    
    def set_employees(self):
        with SessionLocal() as session:
            repo = SearchEmployeeSkillRepository(session)
            service = SearchEmployeeSkillsService(repo)
            self.employees = service.fetch_employee_skills()
    

    def main_menu(self):
        with SessionLocal() as session:
            repo = SkillRepository(session)
            service = SkillService(repo)
            skills = service.get_all_for_crud()
        self.set_employees()
        sesm.main_menu(self.employees, self.requisite, skills)
