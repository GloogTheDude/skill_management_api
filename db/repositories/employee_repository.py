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
