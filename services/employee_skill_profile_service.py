from datetime import date

from sqlalchemy.exc import NoResultFound

from core.constants import SKILLSOURCETYPE
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.skill_dto import CurrentSkillValidationDTO, SkillProfileDTO, SkillSourceDTO
from models.skill import Skill
from services.skill_profile_aggregation import (
    add_skill_source,
)
from dto.auth_dto import AuthEmployeeDTO
from services.employee_authorization_service import EmployeeAuthorizationService


class EmployeeSkillProfileService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        acquisition_repository: AcquisitionSkillRepository,
    ):
        self.employee_repository = employee_repository
        self.acquisition_repository = acquisition_repository

    def get_profile(
        self, id_employee: int, current_employee: AuthEmployeeDTO | None = None
    ) -> list[SkillProfileDTO]:
        employee = self.employee_repository.get_one(id_employee)
        if employee.is_deleted:
            raise NoResultFound()
        if current_employee is not None:
            EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
                current_employee, employee
            )

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

        self._finalize_profiles(profiles)

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
        for skill_validation, skill, domaine, validator in rows:
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
            profile = profiles[skill.id_skill]
            profile.evaluated_level = skill_validation.level_skill
            profile.current_validation = CurrentSkillValidationDTO(
                id_skill_validation=skill_validation.id_skill_validation,
                level=skill_validation.level_skill,
                validated_at=skill_validation.validated_at,
                justification=skill_validation.justification,
                id_validator=skill_validation.id_validator,
                validator_first_name=validator.first_name,
                validator_last_name=validator.last_name,
                id_validation=skill_validation.id_validation,
            )

    @staticmethod
    def _finalize_profiles(profiles: dict[int, SkillProfileDTO]) -> None:
        for profile in profiles.values():
            acquired = [
                source for source in profile.sources
                if source.source_type != SKILLSOURCETYPE.VALIDATION.value
                and source.is_active
            ]
            profile.acquired_sources = [
                source for source in profile.sources
                if source.source_type != SKILLSOURCETYPE.VALIDATION.value
            ]
            profile.acquired_level = max(
                (source.level for source in acquired if source.level is not None),
                default=None,
            )
            if acquired:
                profile.primary_acquired_source = sorted(
                    acquired,
                    key=lambda source: (
                        source.level is not None,
                        source.level if source.level is not None else -1,
                        source.acquired_at or date.min,
                        source.source_type,
                        source.source_id,
                    ),
                    reverse=True,
                )[0]

    @classmethod
    def _add_source(
        cls,
        profiles: dict[int, SkillProfileDTO],
        skill: Skill,
        domaine: str | None,
        source: SkillSourceDTO,
    ) -> None:
        add_skill_source(
            profiles,
            skill_id=skill.id_skill,
            skill_name=skill.name_skill,
            skill_domaine=domaine,
            source=source,
        )
