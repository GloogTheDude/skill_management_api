from core.database import SessionLocal
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from menus.employee_menu import EmployeeMenu
from db.repositories.skills_repository import SkillRepository
from services.skill_service import SkillService
from db.repositories.certification_repository import CertificationRepository
from services.certification_service import CertificationService
from dto.employee_dto import EmployeeDTO
from menus.manager_menu import ManagerMenu
from controllers.training_request_controller import TrainingRequestController

class ManagerController():
    
    def __init__(self,manager: EmployeeDTO):
        self.manager = manager
        self.training_request_controller = TrainingRequestController(self.manager)

    def get_main_manager_menu(self):
        em = EmployeeMenu()
        mm = ManagerMenu()
        user_choice = -1
        while user_choice != 0:
            user_choice = mm.main_menu()
            match user_choice:
                case 1: #1. see skills
                    with SessionLocal() as session:
                        repo = SkillRepository(session)
                        acquisitionRepo = AcquisitionSkillRepository(session)
                        service = SkillService(repo, acquisitionRepo)

                        skills= acquisitionRepo.get_trainingskills_by_id_employee(self.manager.id_employee)
                    em.display_skills(skills_employee=skills)
                case 2: 
                    with SessionLocal() as session:
                        repo = CertificationRepository(session)
                        service = CertificationService(repo)
                        certifications_employee = service.fetch_certification_employee(self.manager.id_employee)
                    em.display_certification(certifications_employee)
                case 3: #3. ask for training
                    self.training_request_controller.get_training_request_menu()
                case 4:
                    self.training_request_controller.follow_up_request()
                case 5:
                    #subordonate request to (in)validate
                    self.training_request_controller.manage_pending_requests_for_manager(self.manager)
                case 0:
                    return 
                
    
