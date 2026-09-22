from dto.domaine_dto import (
    CreateDomaineDTO,
    UpdateDomaineDTO,
    ResponseDomaineDTO,
)
from models.domaine import Domaine
from services.base_crud_service import BaseCrudService


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

    def create(
        self,
        dto: CreateDomaineDTO,
    ) -> ResponseDomaineDTO:

        domaine = Domaine(
            nom_domaine=dto.nom_domaine,
            is_deleted=False,
        )

        domaine = self.repository.add(domaine)

        return ResponseDomaineDTO.from_entity(domaine)

    def update(
        self,
        id_domaine: int,
        dto: UpdateDomaineDTO,
    ) -> ResponseDomaineDTO:

        data = dto.model_dump(exclude_unset=True)

        domaine = self.repository.update(
            id_domaine,
            **data,
        )

        return ResponseDomaineDTO.from_entity(domaine)