from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.repositories.base_repository import BaseRepository
from errors.domaine_errors import ErrorIDDomaineMissing
from models.diploma import Diploma
from models.training import Training
from models.domaine import Domaine


class DiplomaRepository(BaseRepository[Diploma]):
    model = Diploma

    def add(self,diploma:Diploma)->Diploma:
        stmt = select(Domaine).where(Domaine.id_domaine == diploma.id_domaine)
        domaine = self._session.scalar(stmt)
        if domaine is None:
            raise ErrorIDDomaineMissing()
        return super().add(diploma)
    
    def update(self, ident:Any ,**kwargs: Any) -> Diploma:
        if "id_domaine" in kwargs:
            stmt = select(Domaine).where(Domaine.id_domaine == kwargs["id_domaine"])
            domaine = self._session.scalar(stmt)
            if domaine is None:
                raise ErrorIDDomaineMissing()
        return super().update(ident,**kwargs)