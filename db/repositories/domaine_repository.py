from sqlalchemy import select
from sqlalchemy.orm import Session

from dto.domaine_dto import ResponseDomaineDTO,QueryDomaineDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from models.domaine import Domaine


class DomaineRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ResponseDomaineDTO]|list:
        stmt = (
            select(Domaine)
            .where(Domaine.is_deleted.is_(False))
            .order_by(Domaine.id_domaine)
        )
        rows = self.session.scalars(stmt).all()
        arr = []
        for r in rows:
            arr.append(ResponseDomaineDTO.from_entity(r))
        return arr

    def get_by_id(self, id_domaine: int) -> Domaine | None:
        return self.session.get(Domaine, id_domaine)

    def add(self, domaine: Domaine) -> Domaine:
        self.session.add(domaine)
        self.session.flush()
        return domaine

    def soft_delete(self, id_domaine: int) -> None:
        domaine = self.get_by_id(id_domaine)
        if domaine is None:
            raise ErrorIDDomaineMissing()
        domaine.is_deleted = True

    def update(self, dto:QueryDomaineDTO): 
        domaine = self.get_by_id(dto.id_domaine)
        
        if domaine is None:
            raise ErrorIDDomaineMissing()

        domaine.nom_domaine = dto.nom_domaine
        return domaine