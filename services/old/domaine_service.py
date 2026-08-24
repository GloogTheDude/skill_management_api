from db.repositories.domaine_repository import DomaineRepository
from models.domaine import Domaine


class DomaineService:
    def __init__(self, domaine_repository: DomaineRepository):
        self.domaine_repository = domaine_repository

    def get_all(self) -> list[Domaine]:
        return self.domaine_repository.get_all()

    def get_by_id(self, id_domaine: int) -> Domaine | None:
        return self.domaine_repository.get_by_id(id_domaine)

    def create(self, nom_domaine: str) -> Domaine:
        domaine = Domaine()
        domaine.nom_domaine = nom_domaine
        domaine.is_deleted = False

        return self.domaine_repository.add(domaine)

    def update(self, id_domaine: int, nom_domaine: str) -> Domaine | None:
        domaine = self.domaine_repository.get_by_id(id_domaine)

        if domaine is None or domaine.is_deleted:
            return None

        domaine.nom_domaine = nom_domaine
        return domaine

    def delete(self, id_domaine: int) -> bool:
        domaine = self.domaine_repository.get_by_id(id_domaine)

        if domaine is None or domaine.is_deleted:
            return False

        self.domaine_repository.soft_delete(domaine)
        return True