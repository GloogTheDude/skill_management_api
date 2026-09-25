from db.repositories.base_repository import BaseRepository
from models.validation_type import ValidationType


class ValidationTypeRepository(BaseRepository[ValidationType]):
    model = ValidationType
