from db.repositories.base_repository import BaseRepository
from models.employee import Employee
from models.role import Role
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee

    def get_active_by_mail(self, mail: str) -> Employee | None:
        statement = (
            select(Employee)
            .options(joinedload(Employee.role).joinedload(Role.access_level))
            .where(
                Employee.mail == mail,
                Employee.is_deleted.is_(False),
            )
        )
        return self._session.scalar(statement)

    def get_active_by_id(self, id_employee: int) -> Employee | None:
        statement = (
            select(Employee)
            .options(joinedload(Employee.role).joinedload(Role.access_level))
            .where(
                Employee.id_employee == id_employee,
                Employee.is_deleted.is_(False),
            )
        )
        return self._session.scalar(statement)

    def get_all_with_details(self) -> list[Employee]:
        statement = (
            select(Employee)
            .options(
                joinedload(Employee.role).joinedload(Role.access_level),
                joinedload(Employee.manager).joinedload(Employee.role).joinedload(Role.access_level),
            )
            .where(Employee.is_deleted.is_(False))
        )
        return list(self._session.scalars(statement).unique().all())

    def get_direct_reports_with_details(self, manager_id: int) -> list[Employee]:
        statement = (
            select(Employee)
            .options(
                joinedload(Employee.role).joinedload(Role.access_level),
                joinedload(Employee.manager),
            )
            .where(
                Employee.id_manager == manager_id,
                Employee.is_deleted.is_(False),
            )
            .order_by(Employee.last_name, Employee.first_name)
        )
        return list(self._session.scalars(statement).unique().all())

    def get_active_manager_targets(self, excluded_id: int) -> list[Employee]:
        statement = select(Employee).where(Employee.is_deleted.is_(False), Employee.id_employee != excluded_id).order_by(Employee.last_name, Employee.first_name)
        return list(self._session.scalars(statement).all())

    def has_active_reports(self, id_manager: int) -> bool:
        statement = select(Employee.id_employee).where(Employee.id_manager == id_manager, Employee.is_deleted.is_(False)).limit(1)
        return self._session.scalar(statement) is not None
