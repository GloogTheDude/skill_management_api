from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from models.training import Training


@dataclass #rework
class ResponseTrainingDTO:
    id_training: int |None
    title: str | None
    domaine_name: str | None
    source_name: str | None
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



class QueryTrainingDTO (BaseModel):
    id_training: int |None
    title: str | None
    id_domaine: int | None
    id_source: int | None
    id_certification: int | None
    id_diploma: int | None
    start_: date | None
    end_: date | None
    cost_hour: Decimal | None
    duration_hours: Decimal | None

class CreateTrainingDTO(BaseModel):
    title: str
    id_domaine: int
    id_source: int
    id_certification: int | None = None
    id_diploma: int | None = None
    start_: date
    end_: date
    cost_hour: float
    duration_hours: int