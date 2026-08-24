
from dataclasses import dataclass

from pydantic import BaseModel, Field

from models.domaine import Domaine


@dataclass 
class ResponseDomaineDTO():
    id_domaine:int
    nom_domaine:str

    @classmethod
    def from_entity(cls:type[ResponseDomaineDTO], domaine:Domaine):
        return cls(
            id_domaine= domaine.id_domaine,
            nom_domaine=domaine.nom_domaine # type: ignore
        )

class QueryDomaineDTO(BaseModel):
    id_domaine:int = Field(gt=0)
    nom_domaine:str = Field(min_length=1)