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
from dto.skill_evaluation_queue_dto import (
    BatchSkillEvaluationDTO,
    EmployeeEvaluationQueueDTO,
    PendingSkillEvaluationDTO,
    SkillEvaluationHistoryDTO,
)
from models.role import Role
from models.validation_type import ValidationType


class SkillValidationService(BaseCrudService[SkillValidation]):

    def get_all(self, employee_id: int | None = None, permission_profile=None) -> list[ResponseSkillValidationDTO]:
        skill_validations = (
            self.repository.get_for_scope(employee_id, permission_profile)
            if employee_id is not None and permission_profile is not None
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

    def get_pending_evaluations(self, employee_id: int, permission_profile):
        return [
            PendingSkillEvaluationDTO(
                id_employee=row.id_employee,
                employee_first_name=row.first_name,
                employee_last_name=row.last_name,
                id_skill=row.id_skill,
                skill_name=row.skill_name,
                skill_domaine=row.skill_domaine,
                acquired_level=row.acquired_level,
                primary_acquired_source=row.primary_acquired_source,
            ) for row in self.repository.get_pending_evaluations_for_scope(employee_id, permission_profile)
        ]

    def get_evaluation_history(self, employee_id: int, permission_profile):
        return [
            SkillEvaluationHistoryDTO(
                id_skill_validation=item.id_skill_validation,
                id_employee=item.id_employee,
                employee_first_name=item.employee.first_name,
                employee_last_name=item.employee.last_name,
                id_skill=item.id_skill,
                skill_name=item.skill.name_skill,
                skill_domaine=item.skill.domaine.nom_domaine if item.skill.domaine else None,
                level_skill=item.level_skill,
                validated_at=item.validated_at,
                superseded_at=item.superseded_at,
                id_validator=item.id_validator,
                validator_first_name=item.validator.first_name if item.validator else None,
                validator_last_name=item.validator.last_name if item.validator else None,
                validation_type_name=item.validation_type.denomination_validation if item.validation_type else None,
                justification=item.justification,
            ) for item in self.repository.get_evaluation_history_for_scope(employee_id, permission_profile)
        ]

    def get_employee_evaluation_queue(self, employee_id: int, permission_profile):
        rows = self.repository.get_employee_evaluation_queue(employee_id, permission_profile)
        roles = {
            role.id_role: role.denomination_role
            for role in self.repository._session.scalars(select(Role)).all()
        }
        return [EmployeeEvaluationQueueDTO(
            id_employee=row.id_employee,
            employee_first_name=row.first_name,
            employee_last_name=row.last_name,
            role_name=roles.get(row.id_role),
            acquired_skills_count=row.acquired_skills_count,
            evaluated_skills_count=row.evaluated_skills_count,
            pending_skills_count=row.acquired_skills_count - row.evaluated_skills_count,
        ) for row in rows]

    def create_batch(self, dto: BatchSkillEvaluationDTO, validator_id: int):
        session = self.repository._session
        target = session.get(Employee, dto.id_employee)
        if target is None or target.is_deleted:
            raise NoResultFound()
        validation_type = session.get(ValidationType, dto.id_validation)
        if validation_type is None or validation_type.is_deleted:
            raise NoResultFound()
        for item in dto.evaluations:
            self.create(
                CreateSkillValidationDTO(
                    id_employee=dto.id_employee,
                    id_skill=item.id_skill,
                    level_skill=item.level_skill,
                    id_validation=dto.id_validation,
                    justification=dto.justification,
                ),
                validator_id,
            )
        return self.get_all(dto.id_employee, None)
