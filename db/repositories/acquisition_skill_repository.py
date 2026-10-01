from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from models.certification import Certification
from models.certification_skill import CertificationSkill
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.employee import Employee
from models.participation import Participation
from models.skill import Skill
from models.skill_validation import SkillValidation
from models.training import Training
from models.training_skill import TrainingSkill
from models.domaine import Domaine
from models.employee_declared_skill import EmployeeDeclaredSkill

from datetime import date

"""dans l'idée c'est:
    1) from an id_employee fetch training where participation = completed and id_diplome = null and id_certificaiton=Null
    2) from thoses fetch trainingXskill
    3) from an id_employee fetch id_employeeXdiploma
    4) from an id_employee fetch id_employeeXcertifation
    5) from an id_employee fetch skill_validation
    6) fuse all collection into a single proper dict of SkillProfileDto"""


class AcquisitionSkillRepository():
    def __init__(self,session):
        self.session = session

    def get_trainingskills_by_id_employee(self, id_employee: int
    ) -> list[tuple[Training, TrainingSkill, Skill, str | None]]:
        sub_query = (
            select(Training.id_training)
            .join(Participation, Participation.id_training == Training.id_training)
            .where(
                Participation.id_employee == id_employee,
                Participation.status == "COMPLETED",
                Participation.is_deleted.is_(False),
                Training.id_diploma.is_(None),
                Training.id_certification.is_(None),
            )
        )

        stmt = (
            select(Training, TrainingSkill, Skill, Domaine.nom_domaine)
            .join(TrainingSkill, TrainingSkill.id_training == Training.id_training)
            .join(Skill, Skill.id_skill == TrainingSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                Training.id_training.in_(sub_query),
                TrainingSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )

        return self.session.execute(stmt).all()
    
    def get_diplomeskills_by_id_employee(self, id_employee: int
    ) -> list[tuple[Diploma, DiplomaSkill, Skill, EmployeeDiploma, str | None]]:
        stmt = (
            select(Diploma, DiplomaSkill, Skill, EmployeeDiploma, Domaine.nom_domaine)
            .join(EmployeeDiploma, EmployeeDiploma.id_diploma == Diploma.id_diploma)
            .join(DiplomaSkill, DiplomaSkill.id_diploma == Diploma.id_diploma)
            .join(Skill, Skill.id_skill == DiplomaSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                EmployeeDiploma.id_employee == id_employee,
                EmployeeDiploma.is_deleted.is_(False),
                Diploma.is_deleted.is_(False),
                DiplomaSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )
        return self.session.execute(stmt).all()

    def get_certificationskill_by_id_employee(self, id_employee: int
    ) -> list[tuple[Certification, CertificationSkill, Skill, EmployeeCertification, str | None]]:
        stmt = (
            select(Certification, CertificationSkill, Skill, EmployeeCertification, Domaine.nom_domaine)
            .join(
                EmployeeCertification,
                EmployeeCertification.id_certification == Certification.id_certification,
            )
            .join(
                CertificationSkill,
                CertificationSkill.id_certification == Certification.id_certification,
            )
            .join(Skill, Skill.id_skill == CertificationSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                EmployeeCertification.id_employee == id_employee,
                EmployeeCertification.is_deleted.is_(False),
                Certification.is_deleted.is_(False),
                CertificationSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )
        return self.session.execute(stmt).all()

    def get_validationskill_by_id_employee(self, id_employee: int
    ) -> list[tuple[SkillValidation, Skill, str | None, object]]:
        stmt = (
            select(SkillValidation, Skill, Domaine.nom_domaine, Employee)
            .join(Skill, Skill.id_skill == SkillValidation.id_skill)
            .join(Employee, Employee.id_employee == SkillValidation.id_validator)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                SkillValidation.id_employee == id_employee,
                SkillValidation.is_deleted.is_(False),
                SkillValidation.superseded_at.is_(None),
                Skill.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
            )
        )
        return self.session.execute(stmt).all()

    def get_declaredskills_by_id_employee(self, id_employee: int):
        stmt = (
            select(EmployeeDeclaredSkill, Skill, Domaine.nom_domaine)
            .join(Skill, Skill.id_skill == EmployeeDeclaredSkill.id_skill)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(
                EmployeeDeclaredSkill.id_employee == id_employee,
                EmployeeDeclaredSkill.is_deleted.is_(False),
                Skill.is_deleted.is_(False),
            )
        )
        return self.session.execute(stmt).all()

   
