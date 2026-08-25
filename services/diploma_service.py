

from dto.diploma_dto import QueryDiplomaDTO, ResponseDiplomaDTO
from models.diploma import Diploma
from services.base_crud_service import BaseCrudService


class DiplomaService(BaseCrudService[Diploma]):

    def get_all(self)->list[ResponseDiplomaDTO]:
        diplomas = self._get_all_entities()
        return [
            ResponseDiplomaDTO.from_entity(diploma)
            for diploma in diplomas
        ]

    def get_by_id(self, id_certif)->ResponseDiplomaDTO:
        diploma = self._get_entity_by_id(id_certif)
        return ResponseDiplomaDTO.from_entity(diploma)

    def create(self, subject_diploma:str, level_diploma:str, id_domaine:int):
        diploma = Diploma(subject_diploma=subject_diploma,
                          level_diploma=level_diploma,
                          id_domaine=id_domaine)
        return ResponseDiplomaDTO.from_entity(self.repository.add(diploma))

    def update(self, dto:QueryDiplomaDTO)->ResponseDiplomaDTO:
        diploma = self.repository.update(dto.id_diploma,
                                         subject_diploma= dto.subject_diploma,
                                         level_diploma= dto.level_diploma,
                                         id_domaine= dto.id_domaine,)
        return ResponseDiplomaDTO.from_entity(diploma)