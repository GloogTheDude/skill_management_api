
from sqlalchemy import select, union_all, func
from sqlalchemy.orm import Session
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


class SearchEmployeeSkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def fetch_skills_employee(self):
        training_stmt = (
            select(
                Employee.id_employee,
                Employee.first_name,
                Employee.last_name,
                Skill.id_skill,
                Skill.name_skill,
                TrainingSkill.granted_level.label("level"),
            )
            .join(Participation, Participation.id_employee == Employee.id_employee)
            .join(Training, Training.id_training == Participation.id_training)
            .join(TrainingSkill, TrainingSkill.id_training == Training.id_training)
            .join(Skill, Skill.id_skill == TrainingSkill.id_skill)
            .where(Employee.is_deleted.is_(False))
            )

        diploma_stmt = (
            select(
                Employee.id_employee,
                Employee.first_name,
                Employee.last_name,
                Skill.id_skill,
                Skill.name_skill,
                DiplomaSkill.min_level.label("level"),
            )
            .join(EmployeeDiploma, EmployeeDiploma.id_employee == Employee.id_employee)
            .join(Diploma, Diploma.id_diploma == EmployeeDiploma.id_diploma)
            .join(DiplomaSkill, DiplomaSkill.id_diploma == Diploma.id_diploma)
            .join(Skill, Skill.id_skill == DiplomaSkill.id_skill)
            .where(Employee.is_deleted.is_(False))
            )   

        certification_stmt = (
            select(
                Employee.id_employee,
                Employee.first_name,
                Employee.last_name,
                Skill.id_skill,
                Skill.name_skill,
                CertificationSkill.granted_level.label("level"),
            )
            .join(EmployeeCertification, EmployeeCertification.id_employee == Employee.id_employee)
            .join(Certification, Certification.id_certification == EmployeeCertification.id_certification)
            .join(CertificationSkill, CertificationSkill.id_certification == Certification.id_certification)
            .join(Skill, Skill.id_skill == CertificationSkill.id_skill)
            .where(EmployeeCertification.expiration > func.current_date(),
                   Employee.is_deleted.is_(False))
            )


        skill_validation_stmt =(
            select(
                Employee.id_employee,
                Employee.first_name,
                Employee.last_name,
                Skill.id_skill,
                Skill.name_skill,
                SkillValidation.level_skill.label("level")
            )
            .join(SkillValidation, SkillValidation.id_employee == Employee.id_employee)
            .join(Skill, Skill.id_skill == SkillValidation.id_skill)
            .where(Employee.is_deleted.is_(False))
        )
        
        employee_skill_sources = union_all(
            training_stmt,
            diploma_stmt,
            certification_stmt,
            skill_validation_stmt
        ).cte("employee_skill_sources")

        stmt = (
            select(
                employee_skill_sources.c.id_employee,
                employee_skill_sources.c.first_name,
                employee_skill_sources.c.last_name,
                employee_skill_sources.c.id_skill,
                employee_skill_sources.c.name_skill,
                func.max(employee_skill_sources.c.level).label("max_level"),
            )
            .group_by(
                employee_skill_sources.c.id_employee,
                employee_skill_sources.c.first_name,
                employee_skill_sources.c.last_name,
                employee_skill_sources.c.id_skill,
                employee_skill_sources.c.name_skill,
            )
            .order_by(
                employee_skill_sources.c.id_employee,
                employee_skill_sources.c.id_skill,
            )
        )

        return self.session.execute(stmt).all()