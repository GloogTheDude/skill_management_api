from pydantic import BaseModel, Field

from models.training_skill import TrainingSkill


class ResponseTrainingSkillDTO(BaseModel):
    id_skill: int
    id_training: int
    granted_level: int
    skill_name: str
    training_title: str

    @classmethod
    def from_entity(
        cls: type["ResponseTrainingSkillDTO"],
        training_skill: TrainingSkill,
    ):
        return cls(
            id_skill=training_skill.id_skill,
            id_training=training_skill.id_training,
            granted_level=training_skill.granted_level,
            skill_name=training_skill.skill.name_skill,
            training_title=training_skill.training.title,
        )


class CreateTrainingSkillDTO(BaseModel):
    id_skill: int = Field(gt=0)
    id_training: int = Field(gt=0)
    granted_level: int = Field(gt=0)


class UpdateTrainingSkillDTO(BaseModel):
    granted_level: int | None = Field(
        default=None,
        gt=0,
    )