from db.repositories.base_repository import BaseRepository
from models.skill_validation import SkillValidation
from models.employee import Employee
from sqlalchemy import select


class SkillValidationRepository(BaseRepository[SkillValidation]):
    model = SkillValidation

    def get_for_scope(self, employee_id: int, access_level: int) -> list[SkillValidation]:
        stmt = select(SkillValidation)
        if access_level != 3:
            stmt = stmt.join(Employee, Employee.id_employee == SkillValidation.id_employee).where(
                Employee.is_deleted.is_(False)
            )
            if access_level == 1:
                stmt = stmt.where(SkillValidation.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (SkillValidation.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(SkillValidation.is_deleted.is_(False))
        return list(self._session.scalars(stmt).all())
