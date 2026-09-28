from datetime import date

from dateutil.relativedelta import relativedelta

from core.constants import CERTIFICATIONSTATUS
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from dto.employee_certification_crud_dto import (
    CreateEmployeeCertificationDTO,
    ResponseEmployeeCertificationDTO,
    UpdateEmployeeCertificationDTO,
)
from dto.employee_certification_expiration_dto import (
    EmployeeCertificationExpirationDTO,
)
from models.employee_certification import EmployeeCertification
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound


class EmployeeCertificationService(
    BaseCrudService[EmployeeCertification]
):

    def get_expiring(self) -> list[EmployeeCertificationExpirationDTO]:
        return self._get_expiring_dtos()

    def _get_expiring_dtos(self) -> list[EmployeeCertificationExpirationDTO]:
        today = date.today()
        result = []

        for employee_certification, employee, certification in self.repository.get_close_to_expiration():
            expiration = employee_certification.expiration
            if expiration < today:
                status = CERTIFICATIONSTATUS.EXPIRED.value
            elif expiration <= today + relativedelta(months=1):
                status = CERTIFICATIONSTATUS.URGENT.value
            else:
                status = CERTIFICATIONSTATUS.EXPIRING_SOON.value

            result.append(
                EmployeeCertificationExpirationDTO(
                    id_employee_certification=employee_certification.id_employee_certification,
                    employee_id=employee.id_employee,
                    employee_first_name=employee.first_name,
                    employee_last_name=employee.last_name,
                    certification_id=certification.id_certification,
                    certification_name=certification.subject_certification,
                    expiration_date=expiration,
                    status=status,
                )
            )

        return result

    def get_all(self, employee_id: int | None = None, access_level: int | None = None) -> list[ResponseEmployeeCertificationDTO]:
        employee_certifications = (
            self.repository.get_for_scope(employee_id, access_level)
            if employee_id is not None and access_level is not None
            else self._get_all_entities()
        )
        return [
            ResponseEmployeeCertificationDTO.from_entity(employee_certification)
            for employee_certification in employee_certifications
        ]

    def get_by_id(
        self,
        id_employee_certification: int,
    ) -> ResponseEmployeeCertificationDTO:
        employee_certification = self._get_entity_by_id(id_employee_certification)
        if employee_certification.is_deleted:
            raise NoResultFound()
        return ResponseEmployeeCertificationDTO.from_entity(employee_certification)

    def create(
        self,
        dto: CreateEmployeeCertificationDTO,
    ) -> ResponseEmployeeCertificationDTO:
        employee_certification = EmployeeCertification(
            id_employee=dto.id_employee,
            id_certification=dto.id_certification,
            start_=dto.start_,
            end_=dto.end_,
            expiration=dto.expiration,
            organism=dto.organism,
            evaluation=dto.evaluation,
            doc=dto.doc,
        )
        created = self.repository.add(employee_certification)
        return ResponseEmployeeCertificationDTO.from_entity(created)

    def update(
        self,
        id_employee_certification: int,
        dto: UpdateEmployeeCertificationDTO,
    ) -> ResponseEmployeeCertificationDTO:
        data = dto.model_dump(exclude_unset=True)
        employee_certification = self.repository.update(
            id_employee_certification,
            **data,
        )
        return ResponseEmployeeCertificationDTO.from_entity(employee_certification)
