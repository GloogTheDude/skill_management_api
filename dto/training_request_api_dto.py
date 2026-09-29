from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CreatePlannedTrainingRequestDTO(BaseModel):
    id_training: int = Field(gt=0)


class CreatePersonalizedTrainingRequestDTO(BaseModel):
    request_desc: str

    @field_validator("request_desc")
    @classmethod
    def validate_request_desc(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("request_desc must not be blank")
        return value


class ApproveTrainingRequestDTO(BaseModel):
    id_training: int | None = Field(default=None, gt=0)


class RejectTrainingRequestDTO(BaseModel):
    reason: str

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reason must not be blank")
        return value


class ResponseTrainingRequestDTO(BaseModel):
    id_training_request: int
    request_desc: str | None
    status: str
    reason: str | None
    requested_at: date
    is_deleted: bool
    id_employee: int
    id_training: int | None
    id_validator: int | None
    training_title: str | None
    domaine_name: str | None
    source_name: str | None = None
    location: str | None = None
    start_: date | None = None
    end_: date | None = None
    duration_hours: Decimal | None = None
    cost_hour: Decimal | None = None


class PendingTrainingRequestDTO(BaseModel):
    id_training_request: int
    request_desc: str | None
    status: str
    reason: str | None
    requested_at: date
    id_employee: int
    first_name_employee: str | None
    last_name_employee: str | None
    id_training: int | None
    training_title: str | None
    domaine_name: str | None
    source_name: str | None
    location: str | None
    start_: date | None
    end_: date | None
    duration_hours: Decimal | None
    cost_hour: Decimal | None
