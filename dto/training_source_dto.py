from pydantic import BaseModel, Field

from models.training_source import TrainingSource


class ResponseTrainingSourceDTO(BaseModel):
    id_source: int
    name_source: str

    @classmethod
    def from_entity(
        cls: type["ResponseTrainingSourceDTO"],
        source: TrainingSource,
    ):
        return cls(
            id_source=source.id_source,
            name_source=source.name_source,
        )


class CreateTrainingSourceDTO(BaseModel):
    name_source: str = Field(
        min_length=1,
        max_length=100,
    )


class UpdateTrainingSourceDTO(BaseModel):
    name_source: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )