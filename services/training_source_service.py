from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_source_dto import QueryTrainingSourceDTO, ResponseTrainingSourceDTO
from models.training_source import TrainingSource
from services.base_crud_service import BaseCrudService


class TrainingSourceService(BaseCrudService[TrainingSource]):

    def create(self, name_source: str) -> TrainingSource:
        training_source = TrainingSource(
            name_source=name_source
        )
        return self.repository.add(training_source)

    def get_all(self) -> list[ResponseTrainingSourceDTO]:
        sources = self._get_all_entities()
        return [
            ResponseTrainingSourceDTO.from_entity(source)
            for source in sources
        ]

    def get_by_id(self,id_training_source: int,) -> ResponseTrainingSourceDTO:
        source = self._get_entity_by_id(id_training_source)
        return ResponseTrainingSourceDTO.from_entity(source)

    def update(self,dto: QueryTrainingSourceDTO) -> TrainingSource:
        return self.repository.update(
            dto.id_source,
            name_source=dto.name_source,
        )