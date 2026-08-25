from dataclasses import dataclass

from pydantic import BaseModel

from models.certification import Certification


@dataclass
class ResponseCertificationDTO:
    id_certification: int
    subject_certification: str | None
    validity_month: int | None
    id_domaine: int | None
    domaine_name: str | None

    @classmethod
    def from_entity(cls:type[ResponseCertificationDTO], certif:Certification):
        return cls(
            id_certification = certif.id_certification,
            subject_certification= certif.subject_certification,
            validity_month=certif.validity_month,
            id_domaine= certif.id_domaine,
            domaine_name=certif.domaine.nom_domaine
        )

class QueryCertificationDTO(BaseModel):
    id_certification: int
    subject_certification: str | None = None
    validity_month: int | None = None
    id_domaine: int


class CreateCertificationDTO(BaseModel):
    subject_certification: str | None = None
    validity_month: int | None = None
    id_domaine: int