from dto.skill_validation_dto import (
    CreateSkillValidationDTO,
    UpdateSkillValidationDTO,
    ResponseSkillValidationDTO,
)
from models.skill_validation import SkillValidation
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound


class SkillValidationService(BaseCrudService[SkillValidation]):

    def get_all(self, employee_id: int | None = None, access_level: int | None = None) -> list[ResponseSkillValidationDTO]:
        skill_validations = (
            self.repository.get_for_scope(employee_id, access_level)
            if employee_id is not None and access_level is not None
            else self._get_all_entities()
        )

        return [
            ResponseSkillValidationDTO.from_entity(skill_validation)
            for skill_validation in skill_validations
        ]

    def get_by_id(
        self,
        id_skill_validation: int,
    ) -> ResponseSkillValidationDTO:
        skill_validation = self._get_entity_by_id(id_skill_validation)
        if skill_validation.is_deleted:
            raise NoResultFound()
        return ResponseSkillValidationDTO.from_entity(skill_validation)

    def create(
        self,
        dto: CreateSkillValidationDTO,
        validator_id: int,
    ) -> ResponseSkillValidationDTO:
        skill_validation = SkillValidation(
            date_=dto.date_,
            level_skill=dto.level_skill,
            id_validation=dto.id_validation,
            id_employee=dto.id_employee,
            id_validator=validator_id,
            id_skill=dto.id_skill,
        )

        created = self.repository.add(skill_validation)
        return ResponseSkillValidationDTO.from_entity(created)

    def update(
        self,
        id_skill_validation: int,
        dto: UpdateSkillValidationDTO,
    ) -> ResponseSkillValidationDTO:
        data = dto.model_dump(exclude_unset=True)

        skill_validation = self.repository.update(
            id_skill_validation,
            **data,
        )

        return ResponseSkillValidationDTO.from_entity(skill_validation)
