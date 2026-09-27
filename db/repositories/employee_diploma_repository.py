from db.repositories.base_repository import BaseRepository
from models.employee_diploma import EmployeeDiploma
from models.employee import Employee
from sqlalchemy import select


class EmployeeDiplomaRepository(BaseRepository[EmployeeDiploma]):
    model = EmployeeDiploma

    def get_for_scope(self, employee_id: int, access_level: int) -> list[EmployeeDiploma]:
        stmt = select(EmployeeDiploma)
        if access_level != 3:
            stmt = stmt.join(Employee, Employee.id_employee == EmployeeDiploma.id_employee).where(
                Employee.is_deleted.is_(False)
            )
            if access_level == 1:
                stmt = stmt.where(EmployeeDiploma.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (EmployeeDiploma.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(EmployeeDiploma.is_deleted.is_(False))
        return list(self._session.scalars(stmt).all())
