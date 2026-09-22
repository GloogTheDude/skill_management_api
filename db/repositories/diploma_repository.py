from db.repositories.base_repository import BaseRepository
from models.diploma import Diploma


class DiplomaRepository(BaseRepository[Diploma]):
    model = Diploma