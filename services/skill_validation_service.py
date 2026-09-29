from dto.skill_validation_dto import (
    CreateSkillValidationDTO,
    UpdateSkillValidationDTO,
    ResponseSkillValidationDTO,
)
from models.skill_validation import SkillValidation
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone
from sqlalchemy import select
from models.employee import Employee
from models.skill import Skill


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
        session = getattr(self.repository, "_session", None)
        now = datetime.now(timezone.utc)
        if session is not None:
            skill = session.get(Skill, dto.id_skill)
            if skill is None or skill.is_deleted:
                raise NoResultFound()
        skill_validation = SkillValidation(
            date_=now.date(),
            validated_at=now,
            level_skill=dto.level_skill,
            id_validation=dto.id_validation,
            id_employee=dto.id_employee,
            id_validator=validator_id,
            id_skill=dto.id_skill,
            justification=dto.justification,
        )

        current = None
        if session is not None:
            current = session.scalar(select(SkillValidation).where(
                SkillValidation.id_employee == dto.id_employee,
                SkillValidation.id_skill == dto.id_skill,
                SkillValidation.is_deleted.is_(False),
                SkillValidation.superseded_at.is_(None),
            ))
        if current is not None:
            current.superseded_at = now

        created = self.repository.add(skill_validation)
        return ResponseSkillValidationDTO.from_entity(created)

    def update(
        self,
        id_skill_validation: int,
        dto: UpdateSkillValidationDTO,
    ) -> ResponseSkillValidationDTO:
        data = dto.model_dump(exclude_unset=True)
        current = self.repository.get_one(id_skill_validation)
        if current.superseded_at is not None:
            raise ValueError("Superseded skill validations are immutable.")
        forbidden = set(data) & {"id_employee", "id_skill", "date_"}
        if forbidden:
            raise ValueError("Employee, skill and audit date cannot be changed on a validation.")

        skill_validation = self.repository.update(
            id_skill_validation,
            **data,
        )

        return ResponseSkillValidationDTO.from_entity(skill_validation)

    def get_history(self, id_employee: int, id_skill: int):
        return [ResponseSkillValidationDTO.from_entity(item) for item in self.repository.get_history(id_employee, id_skill)]
