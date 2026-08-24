from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, EmailStr,Field

from models.skill import Skill


@dataclass
class SkillSourceDTO:
    source_type: str
    source_id: int
    level: int
    is_active: bool
    acquired_at: date | None = None
    expires_at: date | None = None


@dataclass
class SkillProfileDTO:
    skill_id: int
    skill_name: str
    skill_domaine:str
    displayed_level: int
    primary_source: SkillSourceDTO | None
    sources: list[SkillSourceDTO]

@dataclass
class SkillCrudDTO:
    id_skill: int
    name_skill: str
    domaine_name: str | None

class CreateSkillDTO(BaseModel):
    name: str = Field(min_length=1,max_length=100,description='skill\'s name')
    id_domaine:int = Field(description='domaine\'s ID')

@dataclass
class ResponseSkillDTO:
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

class QuerySkillDTO(BaseModel):
    id_skill:int = Field(description="id skill", gt=0)
    name_skill: str = Field(description="name skill", min_length= 1)
    id_domaine:int = Field(description="id domaine", gt=0)