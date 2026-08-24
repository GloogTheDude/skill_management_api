from controllers.certification_controller import CertificationController
from controllers.participation_controller import ParticipationController
from controllers.search_employee_skills_controller import SearchEmployeeSkillsController
from controllers.training_controller import TrainingController
from core.database import SessionLocal
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_certification_repository import EmployeeCertificationRepository
from menus.employee_menu import EmployeeMenu
from db.repositories.skills_repository import SkillRepository
from services.employee_certification_service import EmployeeCertificationService
from services.skill_service import SkillService
from db.repositories.certification_repository import CertificationRepository
from services.certification_service import CertificationService
from dto.employee_dto import EmployeeDTO
from menus.hr_menu import HRMenu 
from menus.employee_certification_menu import EmployeeCertificationMenu as ecm
from controllers.training_request_controller import TrainingRequestController
from controllers.training_source_controller import TrainingSourceController
from controllers.skill_controller import SkillController
from controllers.domaine_controller import DomaineController
from controllers.diploma_controller import DiplomaController
from controllers.employee_crud_controller import EmployeeCrudController
from menus.crud_menu import CrudMenu
class HRController():
    def __init__(self,hr: EmployeeDTO):
        self.hr = hr
        self.training_request_controller = TrainingRequestController(self.hr)

    def get_main_hr_menu(self):
        em = EmployeeMenu()
        hrm = HRMenu()
        user_choice = -1
        while user_choice != 0:
            user_choice = hrm.main_menu()
            match user_choice:
                case 1: #1. see skills
                    with SessionLocal() as session:
                        repo = SkillRepository(session)
                        acquisitionRepo = AcquisitionSkillRepository(session)
                        service = SkillService(repo, acquisitionRepo)
                        skills= acquisitionRepo.get_trainingskills_by_id_employee(self.hr.id_employee)
                    em.display_skills(skills_employee=skills)
                case 2: 
                    with SessionLocal() as session:
                        repo = CertificationRepository(session)
                        service = CertificationService(repo)
                        certifications_employee = service.fetch_certification_employee(self.hr.id_employee)
                    em.display_certification(certifications_employee)
                case 3: #3. ask for training
                    self.training_request_controller.get_training_request_menu()
                case 4:
                    self.training_request_controller.follow_up_request()
                case 5:
                    #need to change to manage_pending_requests_for_hr
                    #subordonate request to (in)validate
                    self.training_request_controller.manage_pending_requests_for_hr(self.hr)
                case 6:
                    participation_controller = ParticipationController()
                    participation_controller.main_menu()
                case 7:
                    #check certification dead or near end of life
                    with SessionLocal() as session:
                        repo = EmployeeCertificationRepository(session)
                        service = EmployeeCertificationService(repo)
                        close_expiration = service.get_close_to_expiration()
                    ecm.display_close_to_expiration(close_expiration)
                case 8:
                    user_choice_crud = -1
                    while user_choice_crud !=0:
                        user_choice_crud = CrudMenu.main_menu()
                        match user_choice_crud:
                            case 1:
                                controller = TrainingSourceController()
                                controller.main_menu()
                            case 2:
                                controller2 = SkillController()
                                controller2.main_menu()
                            case 3:
                                controller3= DomaineController()
                                controller3.main_menu()
                            case 4:
                                controller4 = DiplomaController()
                                controller4.main_menu()
                            case 5:
                                controller5 = CertificationController()
                                controller5.main_menu()
                            case 6:
                                controller6 = TrainingController()
                                controller6.main_menu()
                            case 7:
                                controller7 = EmployeeCrudController()
                                controller7.main_menu()
                            case 0:
                                print("Back")
                            case _: 
                                print ("you shouldn't be here")
                case 9: 
                    search_employee_skills_controller = SearchEmployeeSkillsController()
                    search_employee_skills_controller.main_menu()
                case 0:
                    return 
                case _:
                    print("error")
    
