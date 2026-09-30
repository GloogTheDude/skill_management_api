from db.repositories.base_repository import BaseRepository
from models.skill_validation import SkillValidation
from models.employee import Employee
from sqlalchemy import select
from sqlalchemy import and_, exists, func, literal
from sqlalchemy.orm import joinedload
from models.skill import Skill
from models.domaine import Domaine
from models.training import Training
from models.training_skill import TrainingSkill
from models.participation import Participation
from models.employee_diploma import EmployeeDiploma
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.employee_certification import EmployeeCertification
from models.certification import Certification
from models.certification_skill import CertificationSkill
from datetime import date
from core.constants import PARTICIPATIONSTATUS, SKILLSOURCETYPE
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

    def get_evaluation_history_for_scope(self, employee_id: int, permission_profile):
        permission_profile = coerce_permission_profile(permission_profile)
        stmt = (
            select(SkillValidation)
            .options(
                joinedload(SkillValidation.employee),
                joinedload(SkillValidation.validator),
                joinedload(SkillValidation.validation_type),
                joinedload(SkillValidation.skill).joinedload(Skill.domaine),
            )
            .join(Employee, Employee.id_employee == SkillValidation.id_employee)
            .where(SkillValidation.is_deleted.is_(False), Employee.is_deleted.is_(False))
            .order_by(SkillValidation.validated_at.desc(), SkillValidation.id_skill_validation.desc())
        )
        if permission_profile == PermissionProfile.MANAGER:
            stmt = stmt.where(Employee.id_manager == employee_id)
        elif permission_profile == PermissionProfile.EMPLOYEE:
            stmt = stmt.where(Employee.id_employee == employee_id)
        return list(self._session.scalars(stmt).unique().all())
