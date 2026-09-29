from dto.employee_diploma_dto import (
    CreateEmployeeDiplomaDTO,
    ResponseEmployeeDiplomaDTO,
    UpdateEmployeeDiplomaDTO,
)
from models.employee_diploma import EmployeeDiploma
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound


class EmployeeDiplomaService(BaseCrudService[EmployeeDiploma]):

    def get_all(self, employee_id: int | None = None, permission_profile=None) -> list[ResponseEmployeeDiplomaDTO]:
        employee_diplomas = (
            self.repository.get_for_scope(employee_id, permission_profile)
            if employee_id is not None and permission_profile is not None
            else self._get_all_entities()
        )

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
        if employee_diploma.is_deleted:
            raise NoResultFound()
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
