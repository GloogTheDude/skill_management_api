from fastapi import HTTPException

from db.repositories.skills_repository import SkillRepository
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from errors.domaine_errors import ErrorIDDomaineMissing
from models.certification import Certification
from models.certification_skill import CertificationSkill
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.skill import Skill
from dto.employee_skill_dto import EmployeeSkillDTO 
from dto.skill_dto import SkillCrudDTO, SkillProfileDTO,SkillSourceDTO
from models.skill_validation import SkillValidation
from models.training import Training
from models.training_skill import TrainingSkill
from core.constants import SKILLSOURCETYPE
from datetime import date

class SkillService():
    def __init__(self, skill_repo:SkillRepository, aquisition_skill_repository:AcquisitionSkillRepository = None):
        self.acquisition_skill_repository = aquisition_skill_repository
        self.skill_repository = skill_repo
    
    def get_acquired_skills(self, id_employee)->list[SkillProfileDTO]:
        training_skills = self.acquisition_skill_repository.get_trainingskills_by_id_employee(id_employee)
        certification_skills = self.acquisition_skill_repository.get_certificationskill_by_id_employee(id_employee)
        diploma_skills = self.acquisition_skill_repository.get_diplomeskills_by_id_employee(id_employee)
        validated_skills = self.acquisition_skill_repository.get_validationskill_by_id_employee(id_employee)
        dict_dto={}
        self.get_skillsourcedto_from_training_skill(training_skills, dict_dto)
        self.get_skillsourcedto_from_certification_skill(certification_skills, dict_dto)
        self.get_skillsourcedto_from_diploma_skill(diploma_skills, dict_dto)
        self.get_skillsourcedto_from_validated_skill(validated_skills, dict_dto)
        print(dict_dto)
        print(list(dict_dto.values()))
        return list(dict_dto.values())

    
    def get_skillsourcedto_from_training_skill(self, training_skills: list[tuple[Training, TrainingSkill, Skill]],
                            dict_dto: dict[int, SkillProfileDTO]):
        for training, training_skill, skill,domaine in training_skills:
            source = SkillSourceDTO(
                source_type=SKILLSOURCETYPE.TRAINING.value,
                source_id=training.id_training,
                level=training_skill.granted_level,
                is_active=True,
                acquired_at=None,
                expires_at=None
            )

            self.push_into_dict(source,skill, dict_dto, domaine)
    
    def get_skillsourcedto_from_certification_skill(self, certification_skills: list[tuple[Certification, CertificationSkill, Skill, EmployeeCertification]],
                                dict_dto: dict[int, SkillProfileDTO]):
        for certification, certification_skill, skill, employee_certification, domaine in certification_skills:
            end_ = employee_certification.end_
            start_ = employee_certification.start_
            is_active = end_ is None or end_ >= date.today()

            source = SkillSourceDTO(
                        source_type=SKILLSOURCETYPE.CERTIFICATION.value,
                        source_id=certification.id_certification,
                        level=certification_skill.granted_level,
                        is_active= is_active,
                        acquired_at=start_,
                        expires_at=end_
                    )
            self.push_into_dict(source,skill, dict_dto, domaine)


    def get_skillsourcedto_from_diploma_skill(self, diploma_skills: list[tuple[Diploma, DiplomaSkill, Skill, EmployeeDiploma]],
                                              dict_dto: dict[int, SkillProfileDTO]):
        for diploma, diploma_skill,skill, employee_diploma,domaine in diploma_skills:
            source = SkillSourceDTO(
                source_type=SKILLSOURCETYPE.DIPLOMA.value,
                source_id= diploma.id_diploma,
                level = diploma_skill.min_level,
                is_active= True,
                acquired_at=employee_diploma.end_,
                expires_at= None
            )

            self.push_into_dict(source,skill, dict_dto, domaine)
    
    def get_skillsourcedto_from_validated_skill(self, validated_skills: list[tuple[SkillValidation, Skill]], 
                             dict_dto: dict[int, SkillProfileDTO]):
        for skill_validation, skill, domaine in validated_skills:
            source = SkillSourceDTO(
                source_type=SKILLSOURCETYPE.VALIDATION.value,
                source_id=skill_validation.id_skill_validation,
                level = skill_validation.level_skill,
                is_active= True,
                acquired_at= skill_validation.date_,
                expires_at=None
            )

            self.push_into_dict(source,skill, dict_dto, domaine)

    def push_into_dict(self, source: SkillSourceDTO, skill:Skill, dict_dto: dict[int, SkillProfileDTO], domaine):
        if skill.id_skill not in dict_dto:
            dict_dto[skill.id_skill] = SkillProfileDTO(
                skill_id=skill.id_skill,
                skill_name=skill.name_skill,
                displayed_level=source.level,
                primary_source=source,
                skill_domaine=domaine,
                sources=[source]
            )
        else:    
            profile = dict_dto[skill.id_skill]
            profile.sources.append(source)

            if self.should_replace_primary_source(source, profile.primary_source):
                profile.displayed_level = source.level
                profile.primary_source = source

    def should_replace_primary_source(self, new_source, current_source)->bool:
        if current_source is None:
            return True

        if new_source.is_active and not current_source.is_active:
            return True

        if not new_source.is_active and current_source.is_active:
            return False

        return new_source.level > current_source.level
    
    def get_all(self) -> list[Skill]:
        return self.skill_repository.get_all()

    def get_by_id(self, id_skill: int) -> Skill | None:
        return self.skill_repository.get_by_id(id_skill)

    def create(self, name_skill: str, id_domaine: int | None) -> Skill:
        try:
            return self.skill_repository.add(name_skill,id_domaine)
        except ErrorIDDomaineMissing:
            raise HTTPException(
            status_code=404,
            detail="ID DOMAINE MISSING"
            ) 


    def update(
        self,
        id_skill: int,
        name_skill: str,
        id_domaine: int | None,
    ) -> Skill | None:
        skill = self.skill_repository.get_by_id(id_skill)

        if skill is None or skill.is_deleted:
            return None

        skill.name_skill = name_skill
        skill.id_domaine = id_domaine
        return skill

    def delete(self, id_skill: int) -> bool:
        skill = self.skill_repository.get_by_id(id_skill)

        if skill is None or skill.is_deleted:
            return False

        self.skill_repository.soft_delete(skill)
        return True

    def get_all_for_crud(self) -> list[SkillCrudDTO]:
        rows = self.skill_repository.get_all_for_crud()

        return [
            SkillCrudDTO(
                id_skill=id_skill,
                name_skill=name_skill,
                domaine_name=domaine_name,
            )
            for id_skill, name_skill, domaine_name in rows
        ]