from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from core.constants import PermissionProfile


class EmployeeAuthorizationService:
    @staticmethod
    def require_hr(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.permission_profile != PermissionProfile.HR:
            raise AuthorizationForbidden("Only HR may perform this administrative action.")

    @staticmethod
    def require_self(current_employee: AuthEmployeeDTO, target_employee_id: int) -> None:
        if current_employee.id_employee != target_employee_id:
            raise AuthorizationForbidden("Employees may only access their own data.")

    @staticmethod
    def require_self_or_direct_manager_or_hr(current_employee, target_employee) -> None:
        if current_employee.permission_profile == PermissionProfile.HR:
            return
        if current_employee.id_employee == target_employee.id_employee:
            return
        if current_employee.permission_profile == PermissionProfile.MANAGER and target_employee.id_manager == current_employee.id_employee:
            return
        raise AuthorizationForbidden("Employee is not authorized to access this data.")

    @staticmethod
    def require_manager_or_hr(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.permission_profile not in (PermissionProfile.MANAGER, PermissionProfile.HR):
            raise AuthorizationForbidden("Only managers and HR may perform this search.")

    @staticmethod
    def authorize_action(current_employee: AuthEmployeeDTO, requested_employee) -> None:
        if current_employee.permission_profile == PermissionProfile.HR:
            return
        if current_employee.permission_profile == PermissionProfile.MANAGER and requested_employee.id_manager == current_employee.id_employee:
            return
        raise AuthorizationForbidden("Employee is not authorized for this request.")

    @staticmethod
    def require_manager_queue(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.permission_profile != PermissionProfile.MANAGER:
            raise AuthorizationForbidden("Only managers may access the manager queue.")

    @staticmethod
    def require_hr_queue(current_employee: AuthEmployeeDTO) -> None:
        if current_employee.permission_profile != PermissionProfile.HR:
            raise AuthorizationForbidden("Only HR may access the HR queue.")
