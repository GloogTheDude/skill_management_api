from sqlalchemy import select
from sqlalchemy.orm import Session

from errors.administrative_security_errors import LastHrAdministratorError
from models.access_level import AccessLevel
from models.employee import Employee
from models.role import Role
from core.constants import PermissionProfile


class AdministrativeSecurityService:
    @staticmethod
    def ensure_hr_survives(session: Session, affected_employee_ids: list[int]) -> None:
        current_hr_ids = set(session.scalars(
            select(Employee.id_employee)
            .join(Role, Employee.id_role == Role.id_role)
            .join(AccessLevel, Role.id_access_level == AccessLevel.id_access_level)
            .where(
                Employee.is_deleted.is_(False),
                Role.is_deleted.is_(False),
                AccessLevel.is_deleted.is_(False),
                AccessLevel.permission_profile == PermissionProfile.HR.value,
            )
        ).all())
        if current_hr_ids and current_hr_ids.issubset(set(affected_employee_ids)):
            raise LastHrAdministratorError(
                "The operation would remove the last active HR administrator."
            )

    @staticmethod
    def employees_for_access_level(session: Session, id_access_level: int) -> list[int]:
        return list(session.scalars(
            select(Employee.id_employee)
            .join(Role, Employee.id_role == Role.id_role)
            .where(
                Employee.is_deleted.is_(False),
                Role.is_deleted.is_(False),
                Role.id_access_level == id_access_level,
            )
        ).all())

    @staticmethod
    def employees_for_role(session: Session, id_role: int) -> list[int]:
        return list(session.scalars(
            select(Employee.id_employee)
            .where(
                Employee.is_deleted.is_(False),
                Employee.id_role == id_role,
            )
        ).all())
