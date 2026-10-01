from datetime import date

from pydantic import BaseModel, Field


class CreateEmployeeDeclaredSkillDTO(BaseModel):
    id_employee: int = Field(gt=0)
    id_skill: int = Field(gt=0)
    level: int = Field(ge=1, le=5)
    acquired_at: date | None = None


class UpdateEmployeeDeclaredSkillDTO(BaseModel):
    level: int | None = Field(default=None, ge=1, le=5)
    acquired_at: date | None = None


class ResponseEmployeeDeclaredSkillDTO(BaseModel):
    id_employee_declared_skill: int
    id_employee: int
    id_skill: int
    skill_name: str | None = None
    skill_domaine: str | None = None
    level: int
    acquired_at: date | None = None
