from core.database import SessionLocal
from db.repositories.participation_repository import ParticipationRepository
from models.training import Training
from services.training_service import TrainingService
from models.employee import Employee
from menus.training_request_menu import TrainingRequestMenu
from menus.validation_request_menu import ValidationRequestMenu
from services.training_request_service import TrainingRequestService
from db.repositories.training_request_repository import TrainingRequestRepository
from db.repositories.training_repository import TrainingRepository
from dto.employee_dto import EmployeeDTO
from core.constants import TRAININGREQUESTSTATUS
from dto.training_dto import TrainingSummaryDTO
from dto.training_request_dto import PendingTrainingRequestForManagerDTO
class TrainingRequestController():
    
    def __init__(self,employee: EmployeeDTO):
        self.employee = employee
        self.training_request_menu = TrainingRequestMenu()

    def get_training_request_menu(self):
        domaine_filter = set()
        user_choice = -1

        while user_choice != 0:
            trainings_availables = self.fetch_available_training()
            user_choice = self.training_request_menu.main_menu()

            match user_choice:
                case 0:
                    return
                case 1:
                    self.see_all_info(
                        trainings_availables,
                        domaine_filter
                    )
                case 2:
                    self.select_preplaned_training(
                        trainings_availables,
                        domaine_filter
                    )
                case 3:
                    self.make_personalised_request()
                case 4:
                    self.follow_up_request()

    def fetch_available_training(self):
        with SessionLocal() as session:
            repo = TrainingRepository(session)
            service = TrainingService(repo)

            return service.fetch_available_training(self.employee.id_employee)

    def see_all_info(self, 
                    trainings_availables:dict[int, TrainingSummaryDTO], 
                    domaine_filter:set):
    
        user_choice = -1
        while not (0<=user_choice<=3):
            user_choice = self.training_request_menu.see_all_formation(trainings=trainings_availables,
                                                                  filter= domaine_filter)
            match user_choice:
                case 0:
                    return
                case 1:
                    self.handle_filter_modification(trainings_availables, 
                                                    domaine_filter)
                case 2:
                    self.select_preplaned_training(trainings_availables,
                                                   domaine_filter)
                case 3:
                    self.make_personalised_request()
    
    def add_domaine_to_filter(self, trainings_availables:dict,domaine_filter:set):
        with SessionLocal() as session:
            repo = TrainingRepository(session)
            service = TrainingService(repo)
            domaines:set = service.filter_dto_by_domaine_name(trainings_availables,domaine_filter)
        
        while domaines:
            domaine = self.training_request_menu.add_filter_domaine_menu(domaines)
            if domaine is None:
                return
            domaine_filter.add(domaine)
            domaines.remove(domaine)
        print("No more domaines to filter")
        return
    
    def remove_domaine_from_filter(self,domaine_filter: set[str],):
        if not domaine_filter:
            print("No active domaine filter")
            return
        while domaine_filter:
            domaine = self.training_request_menu.remove_filter_domaine_menu(domaine_filter
            )
            if domaine is None:
                return
            domaine_filter.remove(domaine)

    def handle_filter_modification(self,trainings_availables:dict,domaine_filter:set):
        while True:
            user_input = self.training_request_menu.filter_modifications_menu()
            match user_input:
                case 0:
                    return
                case 1: 
                    self.add_domaine_to_filter(trainings_availables,domaine_filter)
                case 2: 
                    self.remove_domaine_from_filter(domaine_filter)

    def select_preplaned_training(self, trainings_availables, domaine_filter):
        selected_index = self.training_request_menu.select_training_menu(
            trainings_availables,
            domaine_filter
        )

        if selected_index is None:
            return
    
        selected_training = trainings_availables[selected_index]

        with SessionLocal() as session:
            repo = TrainingRequestRepository(session)
            service = TrainingRequestService(repo)

            try:
                service.call_add_request_preplanned_training(self.employee, selected_training)
                session.commit()
            except Exception:
                session.rollback()
                raise
        
    def make_personalised_request(self):
        request_desc = self.training_request_menu.personalised_training_request_menu()
        with SessionLocal() as session:
            repo = TrainingRequestRepository(session)
            service = TrainingRequestService(repo)
            service.call_add_request_personalised_training(self.employee,request_desc)

    def follow_up_request(self):
        with SessionLocal() as session:
            repo = TrainingRequestRepository(session)
            service = TrainingRequestService(repo)
            employee_requests = service.get_employee_request(self.employee)

        while True:
            user_choice = self.training_request_menu.display_employee_requests(employee_requests)
            if user_choice is None:
                return
            self.training_request_menu.display_employee_request_details(user_choice)

    def manage_pending_requests_for_manager(self, manager: EmployeeDTO):
        menu = ValidationRequestMenu()
        pending_requests=[]
        while True:
            with SessionLocal() as session:
                repo = TrainingRequestRepository(session)
                service= TrainingRequestService(repo)
                pending_requests = service.get_pending_request_for_manager(manager.id_employee)

            selected_request = menu.select_pending_request_to_update(pending_requests)

            if selected_request is None:
                return
            
            status_choice = menu.select_new_request_status()
            if status_choice == 0:
                return
            reason = None

            match status_choice:
                case 1:
                    selected_training_id = selected_request.id_training

                    if selected_training_id is None:
                        selected_training_id = self.ask_training_to_link()

                    self.validate_training_request(
                        selected_request,
                        manager,
                        selected_training_id,
    )
                case 2:
                    reason = menu.get_reason()
                    self.refuse_request(
                        selected_request.id_training_request,
                        manager.id_employee,
                        reason,
                    )
                case _:
                    return
    
    def manage_pending_requests_for_hr(self, hr:EmployeeDTO):
        menu = ValidationRequestMenu()
        pending_requests=[]
        while True:
            with SessionLocal() as session:
                repo = TrainingRequestRepository(session)
                service= TrainingRequestService(repo)
                pending_requests = service.get_pending_request_for_hr()

            selected_request = menu.select_pending_request_to_update(pending_requests)

            if selected_request is None:
                return
            
            status_choice = menu.select_new_request_status()
            if status_choice == 0:
                return
            reason = None

            match status_choice:
                case 1:
                    selected_training_id = selected_request.id_training

                    if selected_training_id is None:
                        selected_training_id = self.ask_training_to_link()

                    self.validate_training_request(
                        selected_request,
                        hr,
                        selected_training_id)
                case 2:
                    reason = menu.get_reason()
                    self.refuse_request(
                        selected_request.id_training_request,
                        hr.id_employee,
                        reason)
                case _:
                    return
    
    def validate_training_request(self, selected_request:PendingTrainingRequestForManagerDTO,
                                  hr:EmployeeDTO, 
                                  selected_training_id:int):
        with SessionLocal() as session:
            request_repo = TrainingRequestRepository(session)
            participation_repo = ParticipationRepository(session)

            service = TrainingRequestService(
                request_repo,
                participation_repo,
            )

            try:
                service.validate_training_request(
                    selected_request.id_training_request,
                    hr.id_employee,
                    selected_training_id,
                )
                session.commit()
            except Exception:
                session.rollback()
                raise
    
    def ask_training_to_link(self)->TrainingSummaryDTO:
        availables_trainings = self.fetch_available_training()
        index = self.training_request_menu.select_training_menu(availables_trainings)
        return availables_trainings[index].id_training

    def refuse_request(self, selected_request:PendingTrainingRequestForManagerDTO,
                        validator:EmployeeDTO, 
                        reason):
        with SessionLocal() as session:
            repo = TrainingRequestRepository(session)
            service= TrainingRequestService(repo)
            service.refuse_request(selected_request.id_training_request,
                                    reason,
                                    validator.id_employee)