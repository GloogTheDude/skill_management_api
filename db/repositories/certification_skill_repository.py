from db.repositories.base_repository import BaseRepository
from models.certification_skill import CertificationSkill
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class CertificationSkillRepository(BaseRepository[CertificationSkill]):
    model=CertificationSkill

    def get_all(self):
        statement = select(CertificationSkill).options(
            joinedload(CertificationSkill.certification), joinedload(CertificationSkill.skill)
        ).where(CertificationSkill.is_deleted.is_(False))
        return list(self._session.scalars(statement).all())
