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


class EmployeeService(BaseCrudService[Employee]):
    def __init__(self, repository, role_repository: RoleRepository | None = None):
        super().__init__(repository)
        self.role_repository = role_repository

    def get_all(self) -> list[ResponseEmployeeDTO]:
        employees = self._get_all_entities()

        return [
            ResponseEmployeeDTO.from_entity(employee)
            for employee in employees
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
        if "id_role" in data and self.role_repository is not None:
            role = self.role_repository.get_one(data["id_role"])
            if role.is_deleted:
                raise NoResultFound()

        if "password" in data:
            data["hash_password"] = hash_password(data.pop("password"))

        employee = self.repository.update(
            id_employee,
            **data,
        )

        return ResponseEmployeeDTO.from_entity(employee)
