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
from dto.employee_certification_dto import CloseToExpirationDTO
from models.employee_certification import EmployeeCertification
from services.base_crud_service import BaseCrudService


class EmployeeCertificationService(
    BaseCrudService[EmployeeCertification]
):

    def add(
        self,
        id_employee: int,
        id_certification: int,
        start_: date | None,
        end_: date | None,
        organism: str | None,
        validity_month: int | None,
        evaluation: str | None = None,
    ) -> EmployeeCertification:
        """Keep the legacy completion workflow compatible during migration."""
        expiration = (
            None
            if validity_month is None or end_ is None
            else end_ + relativedelta(months=validity_month)
        )
        employee_certification = EmployeeCertification(
            id_employee=id_employee,
            id_certification=id_certification,
            start_=start_,
            end_=end_,
            expiration=expiration,
            organism=organism,
            evaluation=evaluation,
            is_deleted=False,
        )
        return self.repository.add(employee_certification)

    def get_close_to_expiration(self) -> list[CloseToExpirationDTO]:
        """Keep the legacy HR workflow compatible during migration."""
        today = date.today()
        close_to_expiration = self.repository.get_close_to_expiration()
        result = []

        for employee_certification, employee, certification in close_to_expiration:
            dto = CloseToExpirationDTO(
                employee_id=employee.id_employee,
                employee_first_name=employee.first_name,
                employee_last_name=employee.last_name,
                certification_id=certification.id_certification,
                certification_name=certification.subject_certification,
                expiration_date=employee_certification.expiration,
                status=None,
            )
            if dto.expiration_date < today:
                dto.status = CERTIFICATIONSTATUS.EXPIRED.value
            elif dto.expiration_date <= today + relativedelta(months=1):
                dto.status = CERTIFICATIONSTATUS.URGENT.value
            else:
                dto.status = CERTIFICATIONSTATUS.EXPIRING_SOON.value
            result.append(dto)

        return result

    def get_all(self) -> list[ResponseEmployeeCertificationDTO]:
        employee_certifications = self._get_all_entities()
        return [
            ResponseEmployeeCertificationDTO.from_entity(employee_certification)
            for employee_certification in employee_certifications
        ]

    def get_by_id(
        self,
        id_employee_certification: int,
    ) -> ResponseEmployeeCertificationDTO:
        employee_certification = self._get_entity_by_id(id_employee_certification)
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
