from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import TrainingRequestForbidden


class EmployeeAuthorizationService:
    @staticmethod
    def require_hr(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.access_level != 3:
            raise TrainingRequestForbidden("Only HR may perform this administrative action.")

    @staticmethod
    def require_self(current_employee: AuthEmployeeDTO, target_employee_id: int) -> None:
        if current_employee.id_employee != target_employee_id:
            raise TrainingRequestForbidden("Employees may only access their own data.")

    @staticmethod
    def require_self_or_direct_manager_or_hr(current_employee, target_employee) -> None:
        if current_employee.access_level == 3:
            return
        if current_employee.id_employee == target_employee.id_employee:
            return
        if current_employee.access_level == 2 and target_employee.id_manager == current_employee.id_employee:
            return
        raise TrainingRequestForbidden("Employee is not authorized to access this data.")

    @staticmethod
    def require_manager_or_hr(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.access_level not in (2, 3):
            raise TrainingRequestForbidden("Only managers and HR may perform this search.")

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
