from datetime import date
from pydantic import BaseModel, Field

from models.skill import Skill


class SkillSourceDTO(BaseModel):
    source_type: str
    source_id: int
    level: int | None
    is_active: bool
    acquired_at: date | None = None
    expires_at: date | None = None


class SkillProfileDTO(BaseModel):
    skill_id: int
    skill_name: str
    skill_domaine: str | None
    displayed_level: int | None
    primary_source: SkillSourceDTO | None
    sources: list[SkillSourceDTO]

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
