from db.repositories.base_repository import BaseRepository
from models.diploma_skill import DiplomaSkill
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class DiplomaSkillRepository(BaseRepository[DiplomaSkill]):
    model=DiplomaSkill

    def get_all(self):
        statement = select(DiplomaSkill).options(
            joinedload(DiplomaSkill.diploma), joinedload(DiplomaSkill.skill)
        ).where(DiplomaSkill.is_deleted.is_(False))
        return list(self._session.scalars(statement).all())
