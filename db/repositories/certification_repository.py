from typing import Any

from sqlalchemy import select

from db.repositories.base_repository import BaseRepository
from errors.domaine_errors import ErrorIDDomaineMissing
from models.certification import Certification
from models.domaine import Domaine

class CertificationRepository(BaseRepository[Certification]):
    model = Certification

    def add(self,certification:Certification)->Certification:
        stmt = select(Domaine).where(Domaine.id_domaine == certification.id_domaine)
        domaine = self._session.scalar(stmt)
        if domaine is None:
            raise ErrorIDDomaineMissing()
        return super().add(certification)

    def update(self, ident:Any ,**kwargs: Any) -> Certification:
        if "id_domaine" in kwargs:
            stmt = select(Domaine).where(Domaine.id_domaine == kwargs["id_domaine"])
            domaine = self._session.scalar(stmt)
            if domaine is None:
                raise ErrorIDDomaineMissing()
        return super().update(ident,**kwargs)