from pydantic import BaseModel, Field

from dto.skill_dto import SkillProfileDTO


class SkillSearchRequirementDTO(BaseModel):
    id_skill: int = Field(gt=0)
    min_acquired_level: int | None = Field(default=None, ge=1, le=5)
    min_evaluated_level: int | None = Field(default=None, ge=1, le=5)


class EmployeeSkillSearchRequestDTO(BaseModel):
    requirements: list[SkillSearchRequirementDTO] = Field(min_length=1)


class EmployeeSkillSearchResultDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    skills: list[SkillProfileDTO]
