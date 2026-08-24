from dataclasses import dataclass

from pydantic import BaseModel, Field

from models.training_source import TrainingSource


@dataclass
class ResponseTrainingSourceDTO:
    id_source:int
    name_source:str

    @classmethod
    def from_entity(cls:type[ResponseTrainingSourceDTO], source: TrainingSource):
        return cls(
            id_source=source.id_source,
            name_source=str(source.name_source)
        )

class QueryTrainingSourceDTO(BaseModel):
    id_source:int = Field(description="id Source", gt=0)
    name_source: str = Field(description="name Source", min_length= 1)