

from db.repositories.employee_certification_repository import EmployeeCertificationRepository
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from dto.participation_dto import ParticipationDTO
from models.certification import Certification
from models.employee import Employee
from models.training_source import TrainingSource
from services.employee_certification_service import EmployeeCertificationService
from services.employee_diploma_service import EmployeeDiplomaService
from services.employee_service import EmployeeService
from services.participation_service import ParticipationService

from menus.participation_menu import ParticipationMenu as pm
from core.constants import TYPEPARTICIPATIONDTO
from services.training_service import TrainingService

class CompletionParticipationService(): 
    def __init__(self, repo_participation: ParticipationRepository, repo_training:TrainingRepository, repo_employee:EmployeeRepository, 
                 repo_employee_diploma:EmployeeDiplomaRepository, repo_employee_certification:EmployeeCertificationRepository):
        self.participation_repository = repo_participation
        self.training_repository = repo_training
        self.employee_repository = repo_employee
        self.employee_diploma_repository = repo_employee_diploma
        self.employee_certification_repository = repo_employee_certification

    def complete_participation(self):
        participations_completable={}
        service = ParticipationService(self.participation_repository)
        participations_completable = service.get_participations_completable()
        print("Please choose the training to update: ")
        participation_selected:ParticipationDTO = pm.get_participation_dto(participations_completable)
        print(f"Participation_selected = {participation_selected} ")
        if participation_selected.training_type == TYPEPARTICIPATIONDTO.DIPLOMA.value:
            self.complete_participation_diploma_training(participation_selected)
        elif participation_selected.training_type == TYPEPARTICIPATIONDTO.CERTIFICATION.value:
            self.complete_participation_certification_training(participation_selected) 
        service = ParticipationService(self.participation_repository)
        print(f"try to set as completed with: participation_selected.employee_id : {participation_selected.employee_id}, participation_selected.training_id{participation_selected.training_id})")
        service.set_participation_to_completed(participation_selected.employee_id, participation_selected.training_id)
    


    def complete_participation_diploma_training(self, participation_selected:ParticipationDTO):

        training_service= TrainingService(self.training_repository)
        employee_service = EmployeeService(self.employee_repository)
        training = training_service.get_by_id(participation_selected.training_id)
        employee = employee_service.get_by_id(participation_selected.employee_id)
        diploma_id = training.id_diploma
        training_source:TrainingSource = training.source

        distinction = "GREAT" #need a menu to get the distinction
        
        employee_diploma_service = EmployeeDiplomaService(self.employee_diploma_repository)
        employee_diploma_service.add(employee.id_employee, diploma_id, training.start_, training.end_, distinction, training_source.name_source)


    def complete_participation_certification_training(self, participation_selected:ParticipationDTO):
        training_service= TrainingService(self.training_repository)
        employee_service = EmployeeService(self.employee_repository)
        training = training_service.get_by_id(participation_selected.training_id)
        employee = employee_service.get_by_id(participation_selected.employee_id)
        certification:Certification= training.certification
        training_source:TrainingSource = training.source
        employee_certification_service = EmployeeCertificationService(self.employee_certification_repository)
        employee_certification_service.add(employee.id_employee, certification.id_certification, training.start_, training.end_, training_source.name_source, certification.validity_month)