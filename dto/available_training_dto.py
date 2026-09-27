from datetime import date

from pydantic import BaseModel


class AvailableTrainingDTO(BaseModel):
    id_training: int
    title: str | None
    domaine_name: str
    start_: date | None
    end_: date | None
