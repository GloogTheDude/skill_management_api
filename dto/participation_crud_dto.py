from datetime import date

from pydantic import BaseModel

from models.participation import Participation


class ResponseParticipationDTO(BaseModel):
    id_employee: int
    id_training: int
    status: str

    @classmethod
    def from_entity(cls, participation: Participation):
        return cls(
            id_employee=participation.id_employee,
            id_training=participation.id_training,
            status=participation.status,
        )


class CompletableParticipationDTO(BaseModel):
    id_employee: int
    employee_first_name: str | None
    employee_last_name: str | None
    id_training: int
    training_title: str | None
    training_start: date | None
    training_end: date | None
    participation_status: str
    training_type: str
