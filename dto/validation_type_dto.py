from pydantic import BaseModel, Field

from models.validation_type import ValidationType


class ResponseValidationTypeDTO(BaseModel):
    id_validation: int
    source: str | None
    denomination_validation: str | None

    @classmethod
    def from_entity(
        cls,
        validation_type: ValidationType,
    ):
        return cls(
            id_validation=validation_type.id_validation,
            source=validation_type.source,
            denomination_validation=validation_type.denomination_validation,
        )


class CreateValidationTypeDTO(BaseModel):
    source: str | None = Field(
        default=None,
        max_length=50,
    )
    denomination_validation: str | None = Field(
        default=None,
        max_length=50,
    )


class UpdateValidationTypeDTO(BaseModel):
    source: str | None = Field(
        default=None,
        max_length=50,
    )
    denomination_validation: str | None = Field(
        default=None,
        max_length=50,
    )
