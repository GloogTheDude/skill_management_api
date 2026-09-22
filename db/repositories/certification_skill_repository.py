from db.repositories.base_repository import BaseRepository
from models.certification_skill import CertificationSkill


class CertificationSkillRepository(BaseRepository[CertificationSkill]):
    model=CertificationSkill