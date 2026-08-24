from abc import ABC
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session
from errors.generic_errors import EntityAlreadyDeleted
T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    model:Type[T]

    def __init__(self, session:Session):
        super().__init__()
        self._session = session

    def get_all(self) -> list[T]:
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False)) # type: ignore

        return list(self._session.scalars(stmt).all())

    def get_one(self, ident: Any) -> T:
        return self._session.get_one(self.model, ident)

    def add(self, entity: T) -> T:
        self._session.add(entity)
        self._session.flush()
        return entity

    def update(self, ident:Any ,**kwargs: Any) -> T:
        entity = self.get_one(ident)
        for field, value in kwargs.items():
            setattr(entity, field, value)
        self._session.flush()
        return entity

    def delete(self, ident:Any) -> T:
        entity = self.get_one(ident)
        self._session.delete(entity)
        self._session.flush()
        return entity

    def soft_delete(self, ident: int) -> T:
        entity = self.get_one(ident)

        if not hasattr(entity, "is_deleted"):
            raise AttributeError(
                f"{type(entity).__name__} does not support soft delete"
            )

        if entity.is_deleted: # type: ignore
            raise EntityAlreadyDeleted()

        entity.is_deleted = True  # type: ignore
        self._session.flush()

        return entity