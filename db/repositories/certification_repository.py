from typing import Any

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session


from db.repositories.base_repository import BaseRepository
from errors.domaine_errors import ErrorIDDomaineMissing
from models.domaine import Domaine
from models.employee_certification import EmployeeCertification
from models.certification import Certification 
from models.certification_skill import CertificationSkill
from models.skill import Skill
from models.employee import Employee

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