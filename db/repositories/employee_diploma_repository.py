from db.repositories.base_repository import BaseRepository
from models.employee_diploma import EmployeeDiploma
from models.employee import Employee
from sqlalchemy import select
from core.constants import PermissionProfile, coerce_permission_profile


class EmployeeDiplomaRepository(BaseRepository[EmployeeDiploma]):
    model = EmployeeDiploma

    def get_for_scope(self, employee_id: int, permission_profile) -> list[EmployeeDiploma]:
        permission_profile = coerce_permission_profile(permission_profile)
        stmt = select(EmployeeDiploma)
        if permission_profile != PermissionProfile.HR:
            stmt = stmt.join(Employee, Employee.id_employee == EmployeeDiploma.id_employee).where(
                Employee.is_deleted.is_(False)
            )
            if permission_profile == PermissionProfile.EMPLOYEE:
                stmt = stmt.where(EmployeeDiploma.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (EmployeeDiploma.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(EmployeeDiploma.is_deleted.is_(False))
        return list(self._session.scalars(stmt).all())
