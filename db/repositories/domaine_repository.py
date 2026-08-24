from sqlalchemy import select
from sqlalchemy.orm import Session

from db.repositories.base_repository import BaseRepository
from dto.domaine_dto import ResponseDomaineDTO,QueryDomaineDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from models.domaine import Domaine


class DomaineRepository(BaseRepository[Domaine]):
    model = Domaine