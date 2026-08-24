from typing import Any

from sqlalchemy import select

from db.repositories.base_repository import BaseRepository
from errors.domaine_errors import ErrorIDDomaineMissing
from models.domaine import Domaine
from models.skill import Skill

class SkillRepository(BaseRepository[Skill]):
    model = Skill

    def add(self, skill: Skill) -> Skill:
        stmt = select(Domaine).where(
            Domaine.id_domaine == skill.id_domaine
        )

        domaine = self._session.scalar(stmt)

        if domaine is None:
            raise ErrorIDDomaineMissing()

        return super().add(skill)

    def update(self, ident: Any, **kwargs: Any) -> Skill:
        if "id_domaine" in kwargs:
            stmt = select(Domaine).where(Domaine.id_domaine == kwargs["id_domaine"])
            domaine = self._session.scalar(stmt)
            if domaine is None:
                raise ErrorIDDomaineMissing()
        return super().update(ident, **kwargs)