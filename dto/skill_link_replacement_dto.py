from pydantic import BaseModel, Field, model_validator


class SkillLinkReplacementItemDTO(BaseModel):
    id_skill: int = Field(gt=0)
    level: int | None = None


class ReplaceSkillsDTO(BaseModel):
    skills: list[SkillLinkReplacementItemDTO]

    @model_validator(mode="after")
    def reject_duplicate_skills(self):
        ids = [item.id_skill for item in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("A skill may only appear once in the replacement list.")
        return self


class TrainingSkillReplacementItemDTO(BaseModel):
    id_skill: int = Field(gt=0)
    level: int = Field(gt=0)


class ReplaceTrainingSkillsDTO(BaseModel):
    skills: list[TrainingSkillReplacementItemDTO]

    @model_validator(mode="after")
    def reject_duplicate_skills(self):
        ids = [item.id_skill for item in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("A skill may only appear once in the replacement list.")
        return self
