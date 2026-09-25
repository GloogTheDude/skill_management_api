from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from db.repositories.base_repository import BaseRepository
from models.certification import Certification
from models.employee import Employee
from models.employee_certification import EmployeeCertification


class EmployeeCertificationRepository(BaseRepository[EmployeeCertification]):
    model = EmployeeCertification

    def get_close_to_expiration(
        self,
    ) -> list[tuple[EmployeeCertification, Employee, Certification]]:
        today = date.today()
        limit_future = today + relativedelta(months=6)
        limit_past = today - relativedelta(months=3)

        stmt = (
            select(EmployeeCertification, Employee, Certification)
            .join(Employee, EmployeeCertification.id_employee == Employee.id_employee)
            .join(
                Certification,
                EmployeeCertification.id_certification
                == Certification.id_certification,
            )
            .where(
                EmployeeCertification.expiration.is_not(None),
                EmployeeCertification.expiration >= limit_past,
                EmployeeCertification.expiration <= limit_future,
                EmployeeCertification.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
                Certification.is_deleted.is_(False),
            )
        )
        return list(self._session.execute(stmt).all())
