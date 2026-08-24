from core.database import SessionLocal
from db.repositories.domaine_repository import DomaineRepository
from menus.domaine_menu import DomaineMenu
from services.domaine_service import DomaineService


class DomaineController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = DomaineMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_domaines()
                case 2:
                    self.create_domaine()
                case 3:
                    self.update_domaine()
                case 4:
                    self.delete_domaine()
                case 0:
                    return

    def list_domaines(self) -> None:
        with SessionLocal() as session:
            repo = DomaineRepository(session)
            service = DomaineService(repo)
            domaines = service.get_all()

        DomaineMenu.display_domaines(domaines)

    def create_domaine(self) -> None:
        nom_domaine = DomaineMenu.ask_nom_domaine()

        if not nom_domaine:
            DomaineMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = DomaineRepository(session)
                service = DomaineService(repo)

                service.create(nom_domaine)

                session.commit()
                DomaineMenu.display_success("Domaine created.")
            except Exception:
                session.rollback()
                raise

    def update_domaine(self) -> None:
        id_domaine = DomaineMenu.ask_id_domaine()
        nom_domaine = DomaineMenu.ask_nom_domaine()

        if not nom_domaine:
            DomaineMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = DomaineRepository(session)
                service = DomaineService(repo)

                updated = service.update(id_domaine, nom_domaine)

                if updated is None:
                    session.rollback()
                    DomaineMenu.display_error("Domaine not found.")
                    return

                session.commit()
                DomaineMenu.display_success("Domaine updated.")
            except Exception:
                session.rollback()
                raise

    def delete_domaine(self) -> None:
        id_domaine = DomaineMenu.ask_id_domaine()

        with SessionLocal() as session:
            try:
                repo = DomaineRepository(session)
                service = DomaineService(repo)

                deleted = service.delete(id_domaine)

                if not deleted:
                    session.rollback()
                    DomaineMenu.display_error("Domaine not found.")
                    return

                session.commit()
                DomaineMenu.display_success("Domaine deleted.")
            except Exception:
                session.rollback()
                raise