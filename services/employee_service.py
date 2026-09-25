from dto.employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
    ResponseEmployeeDTO,
)
from models.employee import Employee
from services.base_crud_service import BaseCrudService


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
    ) -> ResponseEmployeeDTO:

        employee = self._get_entity_by_id(id_employee)

        return ResponseEmployeeDTO.from_entity(employee)

    def create(
        self,
        dto: CreateEmployeeDTO,
    ) -> ResponseEmployeeDTO:

        employee = Employee(
            first_name=dto.first_name,
            last_name=dto.last_name,

            # POC: password is currently stored as plain text.
            # Replace this assignment with hashing later.
            hash_password=dto.password,

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

        # API exposes "password", while the ORM model currently uses
        # "hash_password". Keeping this translation here allows hashing
        # to be introduced later without changing the API contract.
        if "password" in data:
            data["hash_password"] = data.pop("password")

        employee = self.repository.update(
            id_employee,
            **data,
        )

        return ResponseEmployeeDTO.from_entity(employee)