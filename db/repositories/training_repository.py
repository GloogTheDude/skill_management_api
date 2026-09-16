from db.repositories.base_repository import BaseRepository
from models.training import Training


class TrainingRepository(BaseRepository[Training]):
    model = Training