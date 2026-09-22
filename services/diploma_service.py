

from dto.diploma_dto import CreateDiplomaDTO, UpdateDiplomaDTO, ResponseDiplomaDTO
from models.diploma import Diploma
from services.base_crud_service import BaseCrudService


class DiplomaService(BaseCrudService[Diploma]):

    def get_all(self)->list[ResponseDiplomaDTO]:
        diplomas = self._get_all_entities()
        return [
            ResponseDiplomaDTO.from_entity(diploma)
            for diploma in diplomas
        ]

    def get_by_id(
        self,
        id_diploma
    )->ResponseDiplomaDTO:
        diploma = self._get_entity_by_id(id_diploma)
        return ResponseDiplomaDTO.from_entity(diploma)

    def create(
        self,
        dto:CreateDiplomaDTO
    )->ResponseDiplomaDTO:
        diploma = Diploma(subject_diploma=dto.subject_diploma,
                          level_diploma=dto.level_diploma,
                          id_domaine=dto.id_domaine)
        return ResponseDiplomaDTO.from_entity(self.repository.add(diploma))

    def update(
        self,
        id_diploma:int,
        dto:UpdateDiplomaDTO
    )->ResponseDiplomaDTO:
        data = dto.model_dump(exclude_unset=True)
        diploma = self.repository.update(id_diploma,
                                        **data)
        return ResponseDiplomaDTO.from_entity(diploma)