from typing import Literal

from pydantic import BaseModel, Field

from dto.skill_dto import SkillProfileDTO


class SkillSearchRequirementDTO(BaseModel):
    id_skill: int = Field(gt=0)
    operator: Literal["gt", "gte", "eq"]
    level: int = Field(ge=1, le=5)


class EmployeeSkillSearchRequestDTO(BaseModel):
    requirements: list[SkillSearchRequirementDTO] = Field(min_length=1)


class EmployeeSkillSearchResultDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    skills: list[SkillProfileDTO]
