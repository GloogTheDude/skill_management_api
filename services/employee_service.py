from dto.employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
    ResponseEmployeeDTO,
)
from models.employee import Employee
from services.base_crud_service import BaseCrudService
from core.security import hash_password
from dto.auth_dto import AuthEmployeeDTO
from services.employee_authorization_service import EmployeeAuthorizationService
from sqlalchemy.exc import NoResultFound
from db.repositories.role_repository import RoleRepository
from services.administrative_security_service import AdministrativeSecurityService
from core.constants import PermissionProfile


class EmployeeService(BaseCrudService[Employee]):
    def __init__(self, repository, role_repository: RoleRepository | None = None):
        super().__init__(repository)
        self.role_repository = role_repository

    def get_all(self) -> list[ResponseEmployeeDTO]:
        employees = self.repository.get_all_with_details()

        return [
            ResponseEmployeeDTO.from_entity(employee)
            for employee in employees
        ]

    def get_direct_reports(self, manager_id: int) -> list[ResponseEmployeeDTO]:
        return [
            ResponseEmployeeDTO.from_entity(employee)
            for employee in self.repository.get_direct_reports_with_details(manager_id)
        ]

    def get_by_id(
        self,
        id_employee: int,
        current_employee: AuthEmployeeDTO | None = None,
    ) -> ResponseEmployeeDTO:

        employee = self._get_entity_by_id(id_employee)
        if employee.is_deleted:
            raise NoResultFound()
        if current_employee is not None:
            EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
                current_employee, employee
            )

        return ResponseEmployeeDTO.from_entity(employee)

    def create(
        self,
        dto: CreateEmployeeDTO,
    ) -> ResponseEmployeeDTO:

        if self.role_repository is not None:
            role = self.role_repository.get_one(dto.id_role)
            if role.is_deleted:
                raise NoResultFound()
        self._validate_manager(dto.id_manager, None)

        employee = Employee(
            first_name=dto.first_name,
            last_name=dto.last_name,

            hash_password=hash_password(dto.password),

            mail=dto.mail,
            id_role=dto.id_role,
            id_manager=dto.id_manager,
        )

        created = self.repository.add(employee)

        return ResponseEmployeeDTO.from_entity(created)

    def update(
        self,
        id_employee: int,
        dto: UpdateEmployeeDTO,
    ) -> ResponseEmployeeDTO:

        data = dto.model_dump(exclude_unset=True)

        if data.get("id_manager") == id_employee:
            raise ValueError("An employee cannot be their own manager.")
        if "id_manager" in data:
            self._validate_manager(data["id_manager"], id_employee)
        if "id_role" in data and self.role_repository is not None:
            current_employee = self.repository.get_one(id_employee)
            role = self.role_repository.get_one(data["id_role"])
            if role.is_deleted:
                raise NoResultFound()
            current_profile = current_employee.role.access_level.permission_profile
            new_profile = role.access_level.permission_profile
            if current_profile in (PermissionProfile.MANAGER.value, PermissionProfile.HR.value) and new_profile not in (PermissionProfile.MANAGER.value, PermissionProfile.HR.value) and self.repository.has_active_reports(id_employee):
                raise ValueError("Cannot change this Employee's profile while they have active direct reports.")
            if current_profile == PermissionProfile.HR.value and new_profile != PermissionProfile.HR.value:
                AdministrativeSecurityService.ensure_hr_survives(self.repository._session, [id_employee])

        if "password" in data:
            data["hash_password"] = hash_password(data.pop("password"))

        employee = self.repository.update(
            id_employee,
            **data,
        )

        return ResponseEmployeeDTO.from_entity(employee)

    def _validate_manager(self, manager_id, employee_id):
        if manager_id is None:
            return
        if not hasattr(self.repository, "get_active_by_id"):
            return
        manager = self.repository.get_active_by_id(manager_id)
        if manager is None:
            raise NoResultFound()
        if manager.role is None or manager.role.access_level is None or manager.role.access_level.permission_profile not in (PermissionProfile.MANAGER.value, PermissionProfile.HR.value):
            raise ValueError("Only Employees with MANAGER or HR permission profile can manage direct reports.")
        if employee_id is None:
            return
        seen = {employee_id}
        current = manager
        while current is not None:
            if current.id_employee in seen:
                raise ValueError("The manager assignment would create a hierarchy cycle.")
            seen.add(current.id_employee)
            current = current.manager

    def delete(self, id_employee: int):
        employee = self.repository.get_one(id_employee)
        if employee.role.access_level.permission_profile == PermissionProfile.HR.value:
            AdministrativeSecurityService.ensure_hr_survives(self.repository._session, [id_employee])
        if self.repository.has_active_reports(id_employee):
            raise ValueError("An employee with active direct reports cannot be archived.")
        return super().delete(id_employee)
