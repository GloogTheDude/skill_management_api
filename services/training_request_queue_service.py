from dto.auth_dto import AuthEmployeeDTO
from dto.training_request_api_dto import PendingTrainingRequestDTO
from db.repositories.training_request_repository import TrainingRequestRepository
from services.employee_authorization_service import EmployeeAuthorizationService


class TrainingRequestQueueService:
    def __init__(self, repository: TrainingRequestRepository):
        self.repository = repository

    def get_for_manager(self, current_employee: AuthEmployeeDTO) -> list[PendingTrainingRequestDTO]:
        EmployeeAuthorizationService.require_manager_queue(current_employee)
        rows = self.repository.get_pending_for_manager(current_employee.id_employee)
        return [self._to_response(*row) for row in rows]

    def get_for_hr(self, current_employee: AuthEmployeeDTO) -> list[PendingTrainingRequestDTO]:
        EmployeeAuthorizationService.require_hr_queue(current_employee)
        rows = self.repository.get_pending_for_hr()
        return [self._to_response(*row) for row in rows]

    def get_history_for_manager(self, current_employee: AuthEmployeeDTO) -> list[PendingTrainingRequestDTO]:
        EmployeeAuthorizationService.require_manager_queue(current_employee)
        rows = self.repository.get_history_for_manager(current_employee.id_employee)
        return [self._to_response(*row) for row in rows]

    def get_history_for_hr(self, current_employee: AuthEmployeeDTO) -> list[PendingTrainingRequestDTO]:
        EmployeeAuthorizationService.require_hr_queue(current_employee)
        rows = self.repository.get_history_for_hr()
        return [self._to_response(*row) for row in rows]

    @staticmethod
    def _to_response(
        request,
        employee,
        training,
        domaine_name,
        source_name,
        location,
        start_,
        end_,
        duration_hours,
        cost_hour,
    ):
        return PendingTrainingRequestDTO(
            id_training_request=request.id_training_request,
            request_desc=request.request_desc,
            status=request.status,
            reason=request.reason,
            requested_at=request.requested_at,
            id_employee=employee.id_employee,
            first_name_employee=employee.first_name,
            last_name_employee=employee.last_name,
            id_training=training.id_training if training else None,
            training_title=training.title if training else None,
            domaine_name=domaine_name,
            source_name=source_name,
            location=location,
            start_=start_,
            end_=end_,
            duration_hours=duration_hours,
            cost_hour=cost_hour,
        )
