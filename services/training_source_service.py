from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_source_dto import CreateTrainingSourceDTO, UpdateTrainingSourceDTO, ResponseTrainingSourceDTO
from models.training_source import TrainingSource
from services.base_crud_service import BaseCrudService


class TrainingSourceService(BaseCrudService[TrainingSource]):

    def create(self, dto:CreateTrainingSourceDTO) -> ResponseTrainingSourceDTO:
        training_source = TrainingSource(
            name_source=dto.name_source
        )
        training_source = self.repository.add(training_source)

        return ResponseTrainingSourceDTO.from_entity(training_source)

    def get_all(self) -> list[ResponseTrainingSourceDTO]:
        sources = self._get_all_entities()
        return [
            ResponseTrainingSourceDTO.from_entity(source)
            for source in sources
        ]

    def get_by_id(self,id_source: int,) -> ResponseTrainingSourceDTO:
        source = self._get_entity_by_id(id_source)
        return ResponseTrainingSourceDTO.from_entity(source)

    def update(self,id_source:int, dto: UpdateTrainingSourceDTO) -> ResponseTrainingSourceDTO:
        data = dto.model_dump(exclude_unset=True)
        training_source = self.repository.update(
            id_source,
            **data,
        )
        return ResponseTrainingSourceDTO.from_entity(training_source)