from dto.employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
    ResponseEmployeeDTO,
)
from models.employee import Employee
from services.base_crud_service import BaseCrudService
from core.security import hash_password
from dto.auth_dto import AuthEmployeeDTO
from services.training_request_authorization import TrainingRequestAuthorization
from sqlalchemy.exc import NoResultFound


class EmployeeService(BaseCrudService[Employee]):

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
            TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
                current_employee, employee
            )

        return ResponseEmployeeDTO.from_entity(employee)

    def create(
        self,
        dto: CreateEmployeeDTO,
    ) -> ResponseEmployeeDTO:

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

        if "password" in data:
            data["hash_password"] = hash_password(data.pop("password"))

        employee = self.repository.update(
            id_employee,
            **data,
        )

        return ResponseEmployeeDTO.from_entity(employee)
