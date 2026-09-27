from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import TrainingRequestForbidden


class TrainingRequestAuthorization:
    @staticmethod
    def authorize_action(current_employee: AuthEmployeeDTO, requested_employee) -> None:
        if current_employee.access_level == 3:
            return
        if current_employee.access_level == 2 and requested_employee.id_manager == current_employee.id_employee:
            return
        raise TrainingRequestForbidden("Employee is not authorized for this request.")

    @staticmethod
    def require_manager_queue(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.access_level != 2:
            raise TrainingRequestForbidden("Only managers may access the manager queue.")

    @staticmethod
    def require_hr_queue(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.access_level != 3:
            raise TrainingRequestForbidden("Only HR may access the HR queue.")
