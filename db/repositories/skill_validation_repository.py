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

    def get_pending_evaluations_for_scope(self, employee_id: int, permission_profile):
        sources = self._acquired_sources_cte()
        current_validation = exists(
            select(1).where(
                SkillValidation.id_employee == sources.c.id_employee,
                SkillValidation.id_skill == sources.c.id_skill,
                SkillValidation.is_deleted.is_(False),
                SkillValidation.superseded_at.is_(None),
            )
        )
        statement = select(
            sources.c.id_employee,
            sources.c.first_name,
            sources.c.last_name,
            sources.c.id_skill,
            sources.c.skill_name,
            sources.c.skill_domaine,
            func.max(sources.c.level).label("acquired_level"),
            func.min(sources.c.source_type).label("primary_acquired_source"),
        ).where(~current_validation)
        if permission_profile == PermissionProfile.MANAGER:
            statement = statement.where(sources.c.id_manager == employee_id)
        elif permission_profile == PermissionProfile.EMPLOYEE:
            statement = statement.where(sources.c.id_employee == employee_id)
        return list(self._session.execute(statement.group_by(
            sources.c.id_employee, sources.c.first_name, sources.c.last_name,
            sources.c.id_skill, sources.c.skill_name, sources.c.skill_domaine,
        )).all())

    def _acquired_sources_cte(self):
        training = select(
            Employee.id_employee.label("id_employee"), Employee.first_name.label("first_name"),
            Employee.last_name.label("last_name"), Employee.id_manager.label("id_manager"),
            Skill.id_skill.label("id_skill"), Skill.name_skill.label("skill_name"),
            Domaine.nom_domaine.label("skill_domaine"), TrainingSkill.granted_level.label("level"),
            literal(SKILLSOURCETYPE.TRAINING.value).label("source_type"),
        ).join(Participation, Participation.id_employee == Employee.id_employee).join(
            Training, Training.id_training == Participation.id_training
        ).join(TrainingSkill, TrainingSkill.id_training == Training.id_training).join(
            Skill, Skill.id_skill == TrainingSkill.id_skill
        ).outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine).where(
            Employee.is_deleted.is_(False), Participation.status == PARTICIPATIONSTATUS.COMPLETED.value,
            Participation.is_deleted.is_(False), Training.is_deleted.is_(False),
            Training.id_diploma.is_(None), Training.id_certification.is_(None),
            TrainingSkill.is_deleted.is_(False), Skill.is_deleted.is_(False), TrainingSkill.granted_level.is_not(None),
        )
        diploma = select(
            Employee.id_employee.label("id_employee"), Employee.first_name.label("first_name"),
            Employee.last_name.label("last_name"), Employee.id_manager.label("id_manager"),
            Skill.id_skill.label("id_skill"), Skill.name_skill.label("skill_name"),
            Domaine.nom_domaine.label("skill_domaine"), DiplomaSkill.min_level.label("level"),
            literal(SKILLSOURCETYPE.DIPLOMA.value).label("source_type"),
        ).join(EmployeeDiploma, EmployeeDiploma.id_employee == Employee.id_employee).join(
            Diploma, Diploma.id_diploma == EmployeeDiploma.id_diploma
        ).join(DiplomaSkill, DiplomaSkill.id_diploma == Diploma.id_diploma).join(
            Skill, Skill.id_skill == DiplomaSkill.id_skill
        ).outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine).where(
            Employee.is_deleted.is_(False), EmployeeDiploma.is_deleted.is_(False),
            Diploma.is_deleted.is_(False), DiplomaSkill.is_deleted.is_(False),
            Skill.is_deleted.is_(False), DiplomaSkill.min_level.is_not(None),
        )
        certification = select(
            Employee.id_employee.label("id_employee"), Employee.first_name.label("first_name"),
            Employee.last_name.label("last_name"), Employee.id_manager.label("id_manager"),
            Skill.id_skill.label("id_skill"), Skill.name_skill.label("skill_name"),
            Domaine.nom_domaine.label("skill_domaine"), CertificationSkill.granted_level.label("level"),
            literal(SKILLSOURCETYPE.CERTIFICATION.value).label("source_type"),
        ).join(EmployeeCertification, EmployeeCertification.id_employee == Employee.id_employee).join(
            Certification, Certification.id_certification == EmployeeCertification.id_certification
        ).join(CertificationSkill, CertificationSkill.id_certification == Certification.id_certification).join(
            Skill, Skill.id_skill == CertificationSkill.id_skill
        ).outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine).where(
            Employee.is_deleted.is_(False), EmployeeCertification.is_deleted.is_(False),
            Certification.is_deleted.is_(False), CertificationSkill.is_deleted.is_(False),
            Skill.is_deleted.is_(False), CertificationSkill.granted_level.is_not(None),
            (EmployeeCertification.expiration.is_(None) | (EmployeeCertification.expiration >= date.today())),
        )
        return training.union_all(diploma, certification).cte("acquired_evaluation_queue")
