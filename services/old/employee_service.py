from db.repositories.employee_repository import EmployeeRepository
from db.repositories.role_repository import RoleRepository
from dto.employee_dto import EmployeeCrudDTO
from models.employee import Employee


class EmployeeService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        role_repository: RoleRepository | None = None,
    ):
        self.employee_repository = employee_repository
        self.role_repository = role_repository

    def get_by_id(self, id_employee: int) -> Employee | None:
        return self.employee_repository.get_by_id(id_employee)

    def get_all_for_crud(self) -> list[EmployeeCrudDTO]:
        rows = self.employee_repository.get_all_for_crud()

        return [
            EmployeeCrudDTO(
                id_employee=id_employee,
                first_name=first_name,
                last_name=last_name,
                mail=mail,
                id_role=id_role,
                role_name=role_name,
                id_manager=id_manager,
                manager_name=(
                    f"{manager_first_name} {manager_last_name}"
                    if manager_first_name or manager_last_name
                    else None
                ),
            )
            for (
                id_employee,
                first_name,
                last_name,
                mail,
                id_role,
                role_name,
                id_manager,
                manager_first_name,
                manager_last_name,
            ) in rows
        ]

    def create(
        self,
        first_name: str,
        last_name: str,
        mail: str,
        hash_password: str,
        id_role: int,
        id_manager: int | None,
    ) -> Employee | None:
        if not self._is_valid_role(id_role):
            return None

        if not self._is_valid_manager(id_manager):
            return None

        existing_employee = self.employee_repository.get_by_mail(mail)

        if existing_employee is not None:
            return None

        employee = Employee()
        employee.first_name = first_name
        employee.last_name = last_name
        employee.mail = mail
        employee.hash_password = hash_password
        employee.id_role = id_role
        employee.id_manager = id_manager
        employee.is_deleted = False

        return self.employee_repository.add(employee)

    def update(
        self,
        id_employee: int,
        first_name: str,
        last_name: str,
        mail: str,
        hash_password: str | None,
        id_role: int,
        id_manager: int | None,
    ) -> Employee | None:
        employee = self.employee_repository.get_by_id(id_employee)

        if employee is None or employee.is_deleted:
            return None

        if not self._is_valid_role(id_role):
            return None

        if id_manager == id_employee:
            return None

        if not self._is_valid_manager(id_manager):
            return None

        existing_employee = self.employee_repository.get_by_mail(mail)

        if (
            existing_employee is not None
            and existing_employee.id_employee != id_employee
        ):
            return None

        employee.first_name = first_name
        employee.last_name = last_name
        employee.mail = mail
        employee.id_role = id_role
        employee.id_manager = id_manager

        if hash_password is not None and hash_password != "":
            employee.hash_password = hash_password

        return employee

    def delete(self, id_employee: int) -> bool:
        employee = self.employee_repository.get_by_id(id_employee)

        if employee is None or employee.is_deleted:
            return False

        self.employee_repository.soft_delete(employee)
        return True

    def _is_valid_role(self, id_role: int) -> bool:
        if self.role_repository is None:
            return True

        role = self.role_repository.get_by_id(id_role)

        return role is not None and not role.is_deleted

    def _is_valid_manager(self, id_manager: int | None) -> bool:
        if id_manager is None:
            return True

        manager = self.employee_repository.get_by_id(id_manager)

        return manager is not None and not manager.is_deleted