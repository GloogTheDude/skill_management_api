from db.repositories.base_repository import BaseRepository
from models.role import Role


class RoleRepository(BaseRepository[Role]):
    model = Role