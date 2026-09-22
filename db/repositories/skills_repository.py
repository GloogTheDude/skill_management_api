from db.repositories.base_repository import BaseRepository
from models.skill import Skill


class SkillRepository(BaseRepository[Skill]):
    model = Skill