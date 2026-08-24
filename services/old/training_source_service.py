from db.repositories.training_source_repository import TrainingSourceRepository
from models.training_source import TrainingSource


class TrainingSourceService:
    def __init__(self, training_source_repository: TrainingSourceRepository):
        self.training_source_repository = training_source_repository

    def get_all(self) -> list[TrainingSource]:
        return self.training_source_repository.get_all()

    def get_by_id(self, id_training_source: int) -> TrainingSource | None:
        return self.training_source_repository.get_by_id(id_training_source)

    def create(self, name_source: str) -> TrainingSource:
        training_source = TrainingSource()
        training_source.name_source = name_source
        training_source.is_deleted = False

        return self.training_source_repository.add(training_source)

    def update(self, id_training_source: int, name_source: str) -> TrainingSource | None:
        training_source = self.training_source_repository.get_by_id(id_training_source)

        if training_source is None or training_source.is_deleted:
            return None

        training_source.name_source = name_source
        return training_source

    def delete(self, id_training_source: int) -> bool:
        training_source = self.training_source_repository.get_by_id(id_training_source)

        if training_source is None or training_source.is_deleted:
            return False

        self.training_source_repository.soft_delete(training_source)
        return True