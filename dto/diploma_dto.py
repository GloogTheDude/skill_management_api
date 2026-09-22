from pydantic import BaseModel, Field

from models.diploma import Diploma


class ResponseDiplomaDTO(BaseModel):
    id_diploma: int
    subject_diploma: str | None
    level_diploma: str | None
    id_domaine: int | None
    domaine_name: str | None

    @classmethod
    def from_entity(
        cls: type["ResponseDiplomaDTO"],
        diploma: Diploma,
    ):
        return cls(
            id_diploma=diploma.id_diploma,
            subject_diploma=diploma.subject_diploma,
            level_diploma=diploma.level_diploma,
            id_domaine=diploma.id_domaine,
            domaine_name=diploma.domaine.nom_domaine,
        )


class CreateDiplomaDTO(BaseModel):
    subject_diploma: str
    level_diploma: str
    id_domaine: int = Field(gt=0)


class UpdateDiplomaDTO(BaseModel):
    subject_diploma: str | None = None
    level_diploma: str | None = None
    id_domaine: int | None = Field(default=None, gt=0)