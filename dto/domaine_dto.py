from pydantic import BaseModel, Field

from models.domaine import Domaine


class ResponseDomaineDTO(BaseModel):
    id_domaine: int
    nom_domaine: str

    @classmethod
    def from_entity(
        cls: type["ResponseDomaineDTO"],
        domaine: Domaine,
    ):
        return cls(
            id_domaine=domaine.id_domaine,
            nom_domaine=domaine.nom_domaine,
        )


class CreateDomaineDTO(BaseModel):
    nom_domaine: str = Field(
        min_length=1,
        max_length=100,
    )


class UpdateDomaineDTO(BaseModel):
    nom_domaine: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )