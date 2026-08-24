from sqlalchemy import select
from sqlalchemy.orm import Session

from db.repositories.base_repository import BaseRepository
from models.training_source import TrainingSource


class TrainingSourceRepository(BaseRepository[TrainingSource]):
    model = TrainingSource