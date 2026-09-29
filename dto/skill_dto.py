from datetime import date, datetime
from pydantic import BaseModel, Field

from models.skill import Skill


class SkillSourceDTO(BaseModel):
    source_type: str
    source_id: int
    level: int | None
    is_active: bool
    acquired_at: date | None = None
    expires_at: date | None = None


class CurrentSkillValidationDTO(BaseModel):
    id_skill_validation: int
    level: int | None
    validated_at: datetime | None = None
    justification: str | None = None
    id_validator: int
    validator_first_name: str | None = None
    validator_last_name: str | None = None
    id_validation: int


class SkillProfileDTO(BaseModel):
    skill_id: int
    skill_name: str
    skill_domaine: str | None
    acquired_level: int | None = None
    evaluated_level: int | None = None
    primary_acquired_source: SkillSourceDTO | None = None
    acquired_sources: list[SkillSourceDTO] = []
    current_validation: CurrentSkillValidationDTO | None = None
    # Transitional fields. Their legacy semantics remain unchanged.
    displayed_level: int | None = None
    primary_source: SkillSourceDTO | None = None
    sources: list[SkillSourceDTO] = []

class CreateSkillDTO(BaseModel):
    name_skill: str = Field(
        min_length=1,
        max_length=100,
        description="Skill's name",
    )
    id_domaine: int = Field(
        gt=0,
        description="Domaine's ID",
    )

class UpdateSkillDTO(BaseModel):
    name_skill:str|None = None
    id_domaine:int|None = None


class ResponseSkillDTO(BaseModel):
    id_skill:int
    name_skill:str
    id_domaine:int
    name_domaine:str

    @classmethod
    def from_entity(cls:type[ResponseSkillDTO], skill:Skill):
        return cls(
            id_skill=skill.id_skill,
            name_skill=skill.name_skill, # type: ignore
            id_domaine= skill.id_domaine,
            name_domaine= skill.domaine.nom_domaine
        )

# class QuerySkillDTO(BaseModel):
#     id_skill:int = Field(description="id skill", gt=0)
#     name_skill: str = Field(description="name skill", min_length= 1)
#     id_domaine:int = Field(description="id domaine", gt=0)
