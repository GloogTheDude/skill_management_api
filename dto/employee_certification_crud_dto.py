from datetime import date
from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator

from models.employee_certification import EmployeeCertification


class ResponseEmployeeCertificationDTO(BaseModel):
    id_employee_certification: int
    id_employee: int
    id_certification: int
    start_: date | None
    end_: date | None
    expiration: date | None
    organism: str | None
    evaluation: str | None
    doc: str | None

    @classmethod
    def from_entity(
        cls,
        employee_certification: EmployeeCertification,
    ):
        return cls(
            id_employee_certification=employee_certification.id_employee_certification,
            id_employee=employee_certification.id_employee,
            id_certification=employee_certification.id_certification,
            start_=employee_certification.start_,
            end_=employee_certification.end_,
            expiration=employee_certification.expiration,
            organism=employee_certification.organism,
            evaluation=employee_certification.evaluation,
            doc=employee_certification.doc,
        )


class CreateEmployeeCertificationDTO(BaseModel):
    id_employee: int = Field(gt=0)
    id_certification: int = Field(gt=0)
    start_: date | None = None
    end_: date | None = None
    expiration: date | None = None
    organism: str | None = Field(default=None, max_length=50)
    evaluation: str | None = Field(default=None, max_length=50)
    doc: str | None = Field(default=None, max_length=255)


class UpdateEmployeeCertificationDTO(BaseModel):
    id_employee: int | None = Field(default=None, gt=0)
    id_certification: int | None = Field(default=None, gt=0)
    start_: date | None = None
    end_: date | None = None
    expiration: date | None = None
    organism: str | None = Field(default=None, max_length=50)
    evaluation: str | None = Field(default=None, max_length=50)
    doc: str | None = Field(default=None, max_length=255)

    _non_nullable_foreign_keys: ClassVar[frozenset[str]] = frozenset(
        {"id_employee", "id_certification"}
    )

    @model_validator(mode="before")
    @classmethod
    def reject_null_foreign_keys(cls, value: Any) -> Any:
        if isinstance(value, dict):
            null_fields = sorted(
                field
                for field in cls._non_nullable_foreign_keys
                if field in value and value[field] is None
            )
            if null_fields:
                fields = ", ".join(null_fields)
                raise ValueError(f"These fields cannot be null: {fields}")
        return value
