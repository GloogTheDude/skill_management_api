from datetime import date, datetime

from pydantic import BaseModel


class SkillEvaluationHistoryDTO(BaseModel):
    id_skill_validation: int
    id_employee: int
    employee_first_name: str | None
    employee_last_name: str | None
    id_skill: int
    skill_name: str
    skill_domaine: str | None
    level_skill: int | None
    validated_at: datetime | None
    superseded_at: datetime | None
    id_validator: int
    validator_first_name: str | None
    validator_last_name: str | None
    validation_type_name: str | None
    justification: str | None


class BatchSkillEvaluationItemDTO(BaseModel):
    id_skill: int
    level_skill: int


class BatchSkillEvaluationDTO(BaseModel):
    id_employee: int
    id_validation: int
    justification: str | None = None
    evaluations: list[BatchSkillEvaluationItemDTO]
