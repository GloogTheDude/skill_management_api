from typing import Generic, TypeVar

from db.repositories.base_repository import BaseRepository

T = TypeVar("T")


class BaseCrudService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    def _get_all_entities(self) -> list[T]:
        return self.repository.get_all()

    def _get_entity_by_id(self, ident: int) -> T:
        return self.repository.get_one(ident)

    def delete(self, ident: int) -> T:
        return self.repository.soft_delete(ident)