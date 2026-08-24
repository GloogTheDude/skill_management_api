from fastapi import HTTPException

from db.repositories.domaine_repository import DomaineRepository
from dto.domaine_dto import ResponseDomaineDTO,QueryDomaineDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from models.domaine import Domaine


class DomaineService:
    def __init__(self, domaine_repository: DomaineRepository):
        self.domaine_repository = domaine_repository

    def get_all(self) -> list[ResponseDomaineDTO]|list:
        return self.domaine_repository.get_all()

    def get_by_id(self, id_domaine: int) -> Domaine | None:
        return self.domaine_repository.get_by_id(id_domaine)

    def create(self, nom_domaine: str) -> Domaine:
        domaine = Domaine()
        domaine.nom_domaine = nom_domaine
        domaine.is_deleted = False

        return self.domaine_repository.add(domaine)

    def update(self, dto:QueryDomaineDTO) -> Domaine | None:
        try:
            return self.domaine_repository.update(dto)
        except ErrorIDDomaineMissing:
            raise HTTPException(
                status_code=404,
                detail='NO DOMAINE FOR THAT ID'
        )

    def delete(self, id_domaine: int) -> bool:
        try:
            self.domaine_repository.soft_delete(id_domaine)
        except ErrorIDDomaineMissing:
            raise HTTPException(
                status_code=404,
                detail='NO DOMAINE FOR THAT ID'
        )
        return True