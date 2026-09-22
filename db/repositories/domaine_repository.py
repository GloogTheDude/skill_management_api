from db.repositories.base_repository import BaseRepository
from models.domaine import Domaine


class DomaineRepository(BaseRepository[Domaine]):
    model = Domaine