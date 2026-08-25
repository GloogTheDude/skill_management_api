from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.repositories.base_repository import BaseRepository
from dto.training_skill_dto import TrainingSkillDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from models.certification import Certification
from models.diploma import Diploma
from models.domaine import Domaine
from models.skill import Skill
from models.training import Training
from models.training_request import TrainingRequest
from models.training_skill import TrainingSkill
from models.training_source import TrainingSource


class TrainingRepository(BaseRepository[Training]):
    model = Training

    def add(self, training:Training)->Training:
        stmt = (select(Domaine)
                .where(
                    Domaine.id_domaine == training.id_domaine))
        domaine = self._session.scalar(stmt)
        if domaine is None:
            raise ErrorIDDomaineMissing()
        return super().add(training)

    def update(self, ident:Any, **kwargs:Any)->Training:
        if "id_domaine" in kwargs:
            stmt = select(Domaine).where(Domaine.id_domaine == kwargs["id_domaine"])
            domaine = self._session.scalar(stmt)
            if domaine is None:
                raise ErrorIDDomaineMissing()
        return super().update(ident,**kwargs)
