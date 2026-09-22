from db.repositories.base_repository import BaseRepository
from models.certification import Certification


class CertificationRepository(BaseRepository[Certification]):
    model = Certification