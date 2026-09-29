from datetime import date

from sqlalchemy import Boolean, Date, and_, cast, literal, or_, select, union_all
from sqlalchemy.orm import Session

from core.constants import PARTICIPATIONSTATUS, SKILLSOURCETYPE
from models.certification import Certification
from models.certification_skill import CertificationSkill
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.participation import Participation
from models.skill import Skill
from models.skill_validation import SkillValidation
from models.training import Training
from models.training_skill import TrainingSkill
from models.domaine import Domaine


class EmployeeSkillSearchRepository:
    def __init__(self, session: Session):
        self.session = session

    def search(self, requirements, manager_id: int | None = None):
        sources = self._source_cte()
        matching_employee_ids = self._matching_employee_ids(sources, requirements)

        stmt = (
            select(sources)
            .where(sources.c.id_employee.in_(matching_employee_ids))
            .order_by(sources.c.id_employee, sources.c.id_skill, sources.c.source_type)
        )
        if manager_id is not None:
            stmt = stmt.where(
                sources.c.id_employee.in_(
                    select(Employee.id_employee).where(Employee.id_manager == manager_id)
                )
            )
        return list(self.session.execute(stmt).all())

    def _source_cte(self):
        training = (
            select(
                Employee.id_employee.label("id_employee"),
                Employee.first_name.label("first_name"),
                Employee.last_name.label("last_name"),
                Skill.id_skill.label("id_skill"),
                Skill.name_skill.label("skill_name"),
                Domaine.nom_domaine.label("skill_domaine"),
                literal(SKILLSOURCETYPE.TRAINING.value).label("source_type"),
                Training.id_training.label("source_id"),
                TrainingSkill.granted_level.label("level"),
                literal(True, type_=Boolean).label("is_active"),
                literal(None, type_=Date).label("acquired_at"),
                literal(None, type_=Date).label("expires_at"),
            )
            .join(Participation, Participation.id_employee == Employee.id_employee)
            .join(Training, Training.id_training == Participation.id_training)
            .join(TrainingSkill, TrainingSkill.id_training == Training.id_training)
            .join(Skill, Skill.id_skill == TrainingSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                Employee.is_deleted.is_(False),
                Participation.status == PARTICIPATIONSTATUS.COMPLETED.value,
                Participation.is_deleted.is_(False),
                Training.id_diploma.is_(None),
                Training.id_certification.is_(None),
                TrainingSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )

        diploma = (
            select(
                Employee.id_employee.label("id_employee"),
                Employee.first_name.label("first_name"),
                Employee.last_name.label("last_name"),
                Skill.id_skill.label("id_skill"),
                Skill.name_skill.label("skill_name"),
                Domaine.nom_domaine.label("skill_domaine"),
                literal(SKILLSOURCETYPE.DIPLOMA.value).label("source_type"),
                Diploma.id_diploma.label("source_id"),
                DiplomaSkill.min_level.label("level"),
                literal(True, type_=Boolean).label("is_active"),
                EmployeeDiploma.end_.label("acquired_at"),
                literal(None, type_=Date).label("expires_at"),
            )
            .join(EmployeeDiploma, EmployeeDiploma.id_employee == Employee.id_employee)
            .join(Diploma, Diploma.id_diploma == EmployeeDiploma.id_diploma)
            .join(DiplomaSkill, DiplomaSkill.id_diploma == Diploma.id_diploma)
            .join(Skill, Skill.id_skill == DiplomaSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                Employee.is_deleted.is_(False),
                EmployeeDiploma.is_deleted.is_(False),
                Diploma.is_deleted.is_(False),
                DiplomaSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )

        certification_expiration = EmployeeCertification.expiration
        certification_active = or_(
            certification_expiration.is_(None),
            certification_expiration >= date.today(),
        )
        certification = (
            select(
                Employee.id_employee.label("id_employee"),
                Employee.first_name.label("first_name"),
                Employee.last_name.label("last_name"),
                Skill.id_skill.label("id_skill"),
                Skill.name_skill.label("skill_name"),
                Domaine.nom_domaine.label("skill_domaine"),
                literal(SKILLSOURCETYPE.CERTIFICATION.value).label("source_type"),
                Certification.id_certification.label("source_id"),
                CertificationSkill.granted_level.label("level"),
                cast(certification_active, Boolean).label("is_active"),
                EmployeeCertification.start_.label("acquired_at"),
                certification_expiration.label("expires_at"),
            )
            .join(
                EmployeeCertification,
                EmployeeCertification.id_employee == Employee.id_employee,
            )
            .join(
                Certification,
                Certification.id_certification == EmployeeCertification.id_certification,
            )
            .join(
                CertificationSkill,
                CertificationSkill.id_certification == Certification.id_certification,
            )
            .join(Skill, Skill.id_skill == CertificationSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                Employee.is_deleted.is_(False),
                EmployeeCertification.is_deleted.is_(False),
                Certification.is_deleted.is_(False),
                CertificationSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )

        validation = (
            select(
                Employee.id_employee.label("id_employee"),
                Employee.first_name.label("first_name"),
                Employee.last_name.label("last_name"),
                Skill.id_skill.label("id_skill"),
                Skill.name_skill.label("skill_name"),
                Domaine.nom_domaine.label("skill_domaine"),
                literal(SKILLSOURCETYPE.VALIDATION.value).label("source_type"),
                SkillValidation.id_skill_validation.label("source_id"),
                SkillValidation.level_skill.label("level"),
                literal(True, type_=Boolean).label("is_active"),
                SkillValidation.date_.label("acquired_at"),
                literal(None, type_=Date).label("expires_at"),
            )
            .join(SkillValidation, SkillValidation.id_employee == Employee.id_employee)
            .join(Skill, Skill.id_skill == SkillValidation.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                Employee.is_deleted.is_(False),
                SkillValidation.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )

        return union_all(training, certification, diploma, validation).cte(
            "employee_skill_sources"
        )

    def _matching_employee_ids(self, sources, requirements):
        requirement_matches = []
        for index, requirement in enumerate(requirements):
            if requirement.operator == "gt":
                comparison = sources.c.level > requirement.level
            elif requirement.operator == "gte":
                comparison = sources.c.level >= requirement.level
            else:
                comparison = sources.c.level == requirement.level

            requirement_matches.append(
                select(sources.c.id_employee)
                .where(
                    and_(
                        sources.c.id_skill == requirement.id_skill,
                        sources.c.is_active.is_(True),
                        sources.c.level.is_not(None),
                        comparison,
                    )
                )
                .distinct()
            )

        if not requirement_matches:
            return select(sources.c.id_employee).where(False)

        matched_employees = requirement_matches[0]
        for requirement_match in requirement_matches[1:]:
            matched_employees = matched_employees.intersect(requirement_match)
        return matched_employees
