from datetime import date
from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator

from models.skill_validation import SkillValidation


class ResponseSkillValidationDTO(BaseModel):
    id_skill_validation: int
    date_: date | None
    level_skill: int | None
    id_validation: int
    id_employee: int
    id_validator: int
    id_skill: int

    @classmethod
    def from_entity(
        cls,
        skill_validation: SkillValidation,
    ):
        return cls(
            id_skill_validation=skill_validation.id_skill_validation,
            date_=skill_validation.date_,
            level_skill=skill_validation.level_skill,
            id_validation=skill_validation.id_validation,
            id_employee=skill_validation.id_employee,
            id_validator=skill_validation.id_validator,
            id_skill=skill_validation.id_skill,
        )


class CreateSkillValidationDTO(BaseModel):
    date_: date | None = None
    level_skill: int | None = None
    id_validation: int = Field(gt=0)
    id_employee: int = Field(gt=0)
    id_validator: int = Field(gt=0)
    id_skill: int = Field(gt=0)


class UpdateSkillValidationDTO(BaseModel):
    date_: date | None = None
    level_skill: int | None = None
    id_validation: int | None = Field(default=None, gt=0)
    id_employee: int | None = Field(default=None, gt=0)
    id_validator: int | None = Field(default=None, gt=0)
    id_skill: int | None = Field(default=None, gt=0)

    _non_nullable_foreign_keys: ClassVar[frozenset[str]] = frozenset({
        "id_validation",
        "id_employee",
        "id_validator",
        "id_skill",
    })

    @model_validator(mode="before")
    @classmethod
    def reject_null_foreign_keys(cls, value: Any) -> Any:
        if isinstance(value, dict):
            null_fields = sorted(
                field
                for field in cls._non_nullable_foreign_keys
                if field in value and value[field] is None
            )

            if null_fields:
                fields = ", ".join(null_fields)
                raise ValueError(
                    f"These fields cannot be null: {fields}"
                )

        return value
