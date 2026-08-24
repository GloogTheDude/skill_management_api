from core.database import SessionLocal
from db.repositories.employee_certification_repository import EmployeeCertificationRepository
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository 
from db.repositories.training_repository import TrainingRepository
from services.completion_participation_service import CompletionParticipationService
from menus.participation_menu import ParticipationMenu as pm

class ParticipationController():
    def __init__(self):
        pass

    def complete_participation(self):
        with SessionLocal() as session:
            repo_participation= ParticipationRepository(session)
            repo_training=TrainingRepository(session)
            repo_employee=EmployeeRepository(session)
            repo_employee_diploma=EmployeeDiplomaRepository(session)
            repo_employee_certification=EmployeeCertificationRepository(session)
            service = CompletionParticipationService(repo_participation, repo_training, repo_employee,repo_employee_diploma, repo_employee_certification)
            service.complete_participation()
            session.commit()

    def main_menu(self):
        user_choice = pm.main_menu()
        match user_choice:
            case 0:
                return
            case 1:
                #complete_participation
                self.complete_participation()
            case 2:
                #change status
                print("Feature still in developpment")
            case 3:
                #create participation
                print("Feature still in developpment")

