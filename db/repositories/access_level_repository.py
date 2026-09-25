from db.repositories.base_repository import BaseRepository
from models.access_level import AccessLevel


class AccessLevelRepository(BaseRepository[AccessLevel]):
    model = AccessLevel