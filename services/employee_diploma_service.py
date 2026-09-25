from datetime import date

from dto.employee_diploma_dto import (
    CreateEmployeeDiplomaDTO,
    ResponseEmployeeDiplomaDTO,
    UpdateEmployeeDiplomaDTO,
)
from models.employee_diploma import EmployeeDiploma
from services.base_crud_service import BaseCrudService


class EmployeeDiplomaService(BaseCrudService[EmployeeDiploma]):

    def add(
        self,
        employee_id: int,
        diploma_id: int,
        start_: date | None,
        end_: date | None,
        distinction: str | None,
        school: str | None,
    ) -> EmployeeDiploma:
        """Keep the legacy completion workflow compatible during migration."""
        employee_diploma = EmployeeDiploma(
            id_employee=employee_id,
            id_diploma=diploma_id,
            start_=start_,
            end_=end_,
            school=school,
            distinction=distinction,
            doc=None,
            is_deleted=False,
        )
        return self.repository.add(employee_diploma)

    def get_all(self) -> list[ResponseEmployeeDiplomaDTO]:
        employee_diplomas = self._get_all_entities()

        return [
            ResponseEmployeeDiplomaDTO.from_entity(employee_diploma)
            for employee_diploma in employee_diplomas
        ]

    def get_by_id(
        self,
        id_employee: int,
        id_diploma: int,
    ) -> ResponseEmployeeDiplomaDTO:
        employee_diploma = self._get_entity_by_id((id_employee, id_diploma))
        return ResponseEmployeeDiplomaDTO.from_entity(employee_diploma)

    def create(
        self,
        dto: CreateEmployeeDiplomaDTO,
    ) -> ResponseEmployeeDiplomaDTO:
        employee_diploma = EmployeeDiploma(
            id_employee=dto.id_employee,
            id_diploma=dto.id_diploma,
            end_=dto.end_,
            school=dto.school,
            start_=dto.start_,
            distinction=dto.distinction,
            doc=dto.doc,
        )

        created = self.repository.add(employee_diploma)
        return ResponseEmployeeDiplomaDTO.from_entity(created)

    def update(
        self,
        id_employee: int,
        id_diploma: int,
        dto: UpdateEmployeeDiplomaDTO,
    ) -> ResponseEmployeeDiplomaDTO:
        data = dto.model_dump(exclude_unset=True)
        employee_diploma = self.repository.update(
            (id_employee, id_diploma),
            **data,
        )

        return ResponseEmployeeDiplomaDTO.from_entity(employee_diploma)
