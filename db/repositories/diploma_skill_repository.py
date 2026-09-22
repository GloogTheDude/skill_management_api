from db.repositories.base_repository import BaseRepository
from models.diploma_skill import DiplomaSkill


class DiplomaSkillRepository(BaseRepository[DiplomaSkill]):
    model=DiplomaSkill
