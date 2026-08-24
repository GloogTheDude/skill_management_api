from db.repositories.domaine_repository import DomaineRepository
from dto.domaine_dto import QueryDomaineDTO, ResponseDomaineDTO
from models.domaine import Domaine

from services.base_service import BaseCrudService  


class DomaineService(BaseCrudService[Domaine]):

    def get_all(self) -> list[ResponseDomaineDTO]:
        domaines = self._get_all_entities()
        return [
            ResponseDomaineDTO.from_entity(domaine)
            for domaine in domaines
        ]

    def get_by_id(self, id_domaine: int) -> ResponseDomaineDTO:
        domaine = self._get_entity_by_id(id_domaine)
        return ResponseDomaineDTO.from_entity(domaine)

    def create(self, nom_domaine: str) -> ResponseDomaineDTO:
        domaine = Domaine(
            nom_domaine=nom_domaine,
            is_deleted=False,
        )
        domaine = self.repository.add(domaine)
        return ResponseDomaineDTO.from_entity(domaine)

    def update(self, dto: QueryDomaineDTO) -> ResponseDomaineDTO:
        domaine = self.repository.update(
            dto.id_domaine,
            nom_domaine=dto.nom_domaine,
        )
        return ResponseDomaineDTO.from_entity(domaine)