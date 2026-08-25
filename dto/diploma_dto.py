from dataclasses import dataclass

from pydantic import BaseModel

from models.diploma import Diploma


@dataclass
class ResponseDiplomaDTO:
    id_diploma: int
    subject_diploma: str | None
    level_diploma: str | None
    id_domaine: int | None
    domaine_name: str | None

    @classmethod
    def from_entity(cls:type[ResponseDiplomaDTO], diploma:Diploma):
        return cls(
            id_diploma = diploma.id_diploma,
            subject_diploma = diploma.subject_diploma,
            level_diploma= diploma.level_diploma,
            id_domaine= diploma.id_diploma,
            domaine_name= diploma.domaine.domaine_name)

class QueryDiplomaDTO(BaseModel):
    id_diploma:int|None
    subject_diploma:str
    level_diploma:str
    id_domaine:int

