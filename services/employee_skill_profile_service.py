from datetime import date

from sqlalchemy.exc import NoResultFound

from core.constants import SKILLSOURCETYPE
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.skill_dto import SkillProfileDTO, SkillSourceDTO
from models.skill import Skill


class EmployeeSkillProfileService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        acquisition_repository: AcquisitionSkillRepository,
    ):
        self.employee_repository = employee_repository
        self.acquisition_repository = acquisition_repository

    def get_profile(self, id_employee: int) -> list[SkillProfileDTO]:
        employee = self.employee_repository.get_one(id_employee)
        if employee.is_deleted:
            raise NoResultFound()

        profiles: dict[int, SkillProfileDTO] = {}

        self._add_training_sources(
            self.acquisition_repository.get_trainingskills_by_id_employee(
                id_employee
            ),
            profiles,
        )
        self._add_certification_sources(
            self.acquisition_repository.get_certificationskill_by_id_employee(
                id_employee
            ),
            profiles,
        )
        self._add_diploma_sources(
            self.acquisition_repository.get_diplomeskills_by_id_employee(
                id_employee
            ),
            profiles,
        )
        self._add_validation_sources(
            self.acquisition_repository.get_validationskill_by_id_employee(
                id_employee
            ),
            profiles,
        )

        return list(profiles.values())

    def _add_training_sources(self, rows, profiles):
        for training, training_skill, skill, domaine in rows:
            self._add_source(
                profiles,
                skill,
                domaine,
                SkillSourceDTO(
                    source_type=SKILLSOURCETYPE.TRAINING.value,
                    source_id=training.id_training,
                    level=training_skill.granted_level,
                    is_active=True,
                ),
            )

    def _add_certification_sources(self, rows, profiles):
        for certification, certification_skill, skill, employee_certification, domaine in rows:
            expiration = employee_certification.expiration
            is_active = expiration is None or expiration >= date.today()
            self._add_source(
                profiles,
                skill,
                domaine,
                SkillSourceDTO(
                    source_type=SKILLSOURCETYPE.CERTIFICATION.value,
                    source_id=certification.id_certification,
                    level=certification_skill.granted_level,
                    is_active=is_active,
                    acquired_at=employee_certification.start_,
                    expires_at=expiration,
                ),
            )

    def _add_diploma_sources(self, rows, profiles):
        for diploma, diploma_skill, skill, employee_diploma, domaine in rows:
            self._add_source(
                profiles,
                skill,
                domaine,
                SkillSourceDTO(
                    source_type=SKILLSOURCETYPE.DIPLOMA.value,
                    source_id=diploma.id_diploma,
                    level=diploma_skill.min_level,
                    is_active=True,
                    acquired_at=employee_diploma.end_,
                ),
            )

    def _add_validation_sources(self, rows, profiles):
        for skill_validation, skill, domaine in rows:
            self._add_source(
                profiles,
                skill,
                domaine,
                SkillSourceDTO(
                    source_type=SKILLSOURCETYPE.VALIDATION.value,
                    source_id=skill_validation.id_skill_validation,
                    level=skill_validation.level_skill,
                    is_active=True,
                    acquired_at=skill_validation.date_,
                ),
            )

    @classmethod
    def _add_source(
        cls,
        profiles: dict[int, SkillProfileDTO],
        skill: Skill,
        domaine: str | None,
        source: SkillSourceDTO,
    ) -> None:
        profile = profiles.get(skill.id_skill)
        if profile is None:
            profiles[skill.id_skill] = SkillProfileDTO(
                skill_id=skill.id_skill,
                skill_name=skill.name_skill,
                skill_domaine=domaine,
                displayed_level=source.level,
                primary_source=source,
                sources=[source],
            )
            return

        profile.sources.append(source)
        if cls._should_replace_primary_source(source, profile.primary_source):
            profile.primary_source = source
            profile.displayed_level = source.level

    @staticmethod
    def _should_replace_primary_source(
        new_source: SkillSourceDTO,
        current_source: SkillSourceDTO | None,
    ) -> bool:
        if current_source is None:
            return True
        if new_source.is_active != current_source.is_active:
            return new_source.is_active
        if new_source.level is None:
            return False
        if current_source.level is None:
            return True
        return new_source.level > current_source.level
