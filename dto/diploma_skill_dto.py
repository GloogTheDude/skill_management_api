from pydantic import BaseModel, Field

from models.diploma_skill import DiplomaSkill


class ResponseDiplomaSkillDTO(BaseModel):
    id_diploma: int
    id_skill: int
    min_level: int | None
    diploma_name: str | None
    skill_name: str

    @classmethod
    def from_entity(
        cls,
        diploma_skill: DiplomaSkill,
    ):
        return cls(
            id_diploma=diploma_skill.id_diploma,
            id_skill=diploma_skill.id_skill,
            min_level=diploma_skill.min_level,
            diploma_name=diploma_skill.diploma.subject_diploma,
            skill_name=diploma_skill.skill.name_skill,
        )


class CreateDiplomaSkillDTO(BaseModel):
    id_diploma: int = Field(gt=0)
    id_skill: int = Field(gt=0)
    min_level: int | None = None


class UpdateDiplomaSkillDTO(BaseModel):
    min_level: int | None = None