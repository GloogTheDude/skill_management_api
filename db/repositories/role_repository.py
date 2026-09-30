from db.repositories.base_repository import BaseRepository
from models.role import Role
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class RoleRepository(BaseRepository[Role]):
    model = Role

    def get_all(self) -> list[Role]:
        return list(self._session.scalars(
            select(Role).options(joinedload(Role.access_level)).where(Role.is_deleted.is_(False))
        ).all())

    def get_one(self, ident):
        return self._session.scalars(
            select(Role).options(joinedload(Role.access_level)).where(Role.id_role == ident)
        ).one()
