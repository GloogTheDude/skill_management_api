from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator
from dto.skill_link_replacement_dto import TrainingSkillReplacementItemDTO

from models.training import Training


class ResponseTrainingDTO(BaseModel):
    id_training: int
    title: str | None 
    domaine_name: str | None
    source_name: str | None
    location: str | None
    certification_name: str | None
    diploma_name: str | None
    start_: date | None
    end_: date | None
    cost_hour: Decimal | None
    duration_hours: Decimal | None
    @classmethod
    def from_entity(cls:type[ResponseTrainingDTO], training:Training):
        return cls(
            id_training=training.id_training,
            title=training.title,
            domaine_name=training.domaine.nom_domaine,
            source_name=training.source.name_source,
            location=training.location,
            certification_name=(
                training.certification.subject_certification
                if training.certification
                else None
            ),
            diploma_name=(
                training.diploma.subject_diploma
                if training.diploma
                else None
            ),
            start_=training.start_,
            end_=training.end_,
            cost_hour=training.cost_hour,
            duration_hours=training.duration_hours
        )



class UpdateTrainingDTO (BaseModel):
    title: str | None = None
    id_domaine: int | None = None
    id_source: int | None = None
    location: str | None = Field(default=None, max_length=255)
    id_certification: int | None = None
    id_diploma: int | None = None
    start_: date | None = None
    end_: date | None = None
    cost_hour: Decimal | None = None
    duration_hours: Decimal | None = None
    skills: list[TrainingSkillReplacementItemDTO] | None = None

    @model_validator(mode="after")
    def reject_duplicate_skills(self):
        if self.skills is not None:
            ids = [item.id_skill for item in self.skills]
            if len(ids) != len(set(ids)):
                raise ValueError("A skill may only appear once in the replacement list.")
        return self

class CreateTrainingDTO(BaseModel):
    title: str
    id_domaine: int
    id_source: int
    location: str | None = Field(default=None, max_length=255)
    id_certification: int | None = None
    id_diploma: int | None = None
    start_: date
    end_: date
    cost_hour: Decimal
    duration_hours: Decimal
    skills: list[TrainingSkillReplacementItemDTO] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_duplicate_skills(self):
        ids = [item.id_skill for item in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("A skill may only appear once in the replacement list.")
        return self
