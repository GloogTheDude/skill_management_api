from sqlalchemy.exc import NoResultFound

from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from dto.available_training_dto import AvailableTrainingDTO
from dto.auth_dto import AuthEmployeeDTO
from services.training_request_authorization import TrainingRequestAuthorization


class AvailableTrainingService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        training_repository: TrainingRepository,
    ):
        self.employee_repository = employee_repository
        self.training_repository = training_repository

    def get_available_trainings(
        self,
        id_employee: int,
        id_domaine: int | None = None,
        current_employee: AuthEmployeeDTO | None = None,
    ) -> list[AvailableTrainingDTO]:
        employee = self.employee_repository.get_one(id_employee)
        if employee.is_deleted:
            raise NoResultFound()
        if current_employee is not None:
            TrainingRequestAuthorization.require_self(current_employee, id_employee)

        return [
            AvailableTrainingDTO(
                id_training=training.id_training,
                title=training.title,
                domaine_name=domaine_name,
                start_=training.start_,
                end_=training.end_,
            )
            for training, domaine_name in self.training_repository.get_available_for_employee(
                id_employee,
                id_domaine,
            )
        ]
