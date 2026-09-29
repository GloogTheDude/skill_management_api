from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from db.repositories.base_repository import BaseRepository
from models.certification import Certification
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from core.constants import PermissionProfile, coerce_permission_profile


class EmployeeCertificationRepository(BaseRepository[EmployeeCertification]):
    model = EmployeeCertification

    def get_for_scope(self, employee_id: int, permission_profile) -> list[EmployeeCertification]:
        permission_profile = coerce_permission_profile(permission_profile)
        stmt = select(EmployeeCertification)
        if permission_profile != PermissionProfile.HR:
            stmt = stmt.join(Employee, Employee.id_employee == EmployeeCertification.id_employee).where(
                Employee.is_deleted.is_(False)
            )
            if permission_profile == PermissionProfile.EMPLOYEE:
                stmt = stmt.where(EmployeeCertification.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (EmployeeCertification.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(EmployeeCertification.is_deleted.is_(False))
        return list(self._session.scalars(stmt).all())

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
