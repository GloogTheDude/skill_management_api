from db.repositories.base_repository import BaseRepository
from models.skill_validation import SkillValidation
from models.employee import Employee
from sqlalchemy import select
from models.skill import Skill
from core.constants import PermissionProfile, coerce_permission_profile


class SkillValidationRepository(BaseRepository[SkillValidation]):
    model = SkillValidation

    def get_for_scope(self, employee_id: int, permission_profile) -> list[SkillValidation]:
        permission_profile = coerce_permission_profile(permission_profile)
        stmt = select(SkillValidation)
        if permission_profile != PermissionProfile.HR:
            stmt = stmt.join(Employee, Employee.id_employee == SkillValidation.id_employee).where(
                Employee.is_deleted.is_(False)
            )
            if permission_profile == PermissionProfile.EMPLOYEE:
                stmt = stmt.where(SkillValidation.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (SkillValidation.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(SkillValidation.is_deleted.is_(False))
        return list(self._session.scalars(stmt).all())

    def get_history(self, id_employee: int, id_skill: int) -> list[SkillValidation]:
        stmt = (
            select(SkillValidation)
            .where(
                SkillValidation.id_employee == id_employee,
                SkillValidation.id_skill == id_skill,
                SkillValidation.is_deleted.is_(False),
            )
            .order_by(
                SkillValidation.validated_at.desc().nullslast(),
                SkillValidation.id_skill_validation.desc(),
            )
        )
        return list(self._session.scalars(stmt).all())
