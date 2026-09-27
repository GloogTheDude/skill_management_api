from core.database import SessionLocal
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from models.employee import Employee
from menus.employee_menu import EmployeeMenu
from db.repositories.skills_repository import SkillRepository
from services.skill_service import SkillService
from db.repositories.certification_repository import CertificationRepository
from services.certification_service import CertificationService
from services.training_service import TrainingService
from db.repositories.training_repository import TrainingRepository
from dto.employee_dto import EmployeeDTO

class EmployeeController():
    def __init__(self,emp: EmployeeDTO):
        self.employee = emp

    def get_main_employee_menu(self):
        em = EmployeeMenu()
        user_choice = -1
        while user_choice != 0:
            user_choice = em.main_menu()
            match user_choice:
                case 1: #1. see skills
                    with SessionLocal() as session:
                        repo = SkillRepository(session)
                        acquisitionRepo = AcquisitionSkillRepository(session)
                        service = SkillService(repo, acquisitionRepo)
                        skills= service.get_acquired_skills(self.employee.id_employee)

                    em.display_skills(skills_employee=skills)
                case 2: 
                    with SessionLocal() as session:
                        repo = CertificationRepository(session)
                        service = CertificationService(repo)
                        certifications_employee = service.fetch_certification_employee(self.employee.id_employee)
                    em.display_certification(certifications_employee)
                case 0:
                    return
