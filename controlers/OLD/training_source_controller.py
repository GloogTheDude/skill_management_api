from core.database import SessionLocal
from db.repositories.training_source_repository import TrainingSourceRepository
from menus.training_source_menu import TrainingSourceMenu
from services.training_source_service import TrainingSourceService


class TrainingSourceController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = TrainingSourceMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_training_sources()
                case 2:
                    self.create_training_source()
                case 3:
                    self.update_training_source()
                case 4:
                    self.delete_training_source()
                case 0:
                    return

    def list_training_sources(self) -> None:
        with SessionLocal() as session:
            repo = TrainingSourceRepository(session)
            service = TrainingSourceService(repo)

            training_sources = service.get_all()

        TrainingSourceMenu.display_training_sources(training_sources)

    def create_training_source(self) -> None:
        name_source = TrainingSourceMenu.ask_name_source()

        if not name_source:
            TrainingSourceMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = TrainingSourceRepository(session)
                service = TrainingSourceService(repo)

                service.create(name_source)

                session.commit()
                TrainingSourceMenu.display_success("Training source created.")
            except Exception:
                session.rollback()
                raise

    def update_training_source(self) -> None:
        id_source = TrainingSourceMenu.ask_id_source()
        name_source = TrainingSourceMenu.ask_name_source()

        if not name_source:
            TrainingSourceMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = TrainingSourceRepository(session)
                service = TrainingSourceService(repo)

                updated = service.update(id_source, name_source)

                if updated is None:
                    session.rollback()
                    TrainingSourceMenu.display_error("Training source not found.")
                    return

                session.commit()
                TrainingSourceMenu.display_success("Training source updated.")
            except Exception:
                session.rollback()
                raise

    def delete_training_source(self) -> None:
        id_source = TrainingSourceMenu.ask_id_source()

        with SessionLocal() as session:
            try:
                repo = TrainingSourceRepository(session)
                service = TrainingSourceService(repo)

                deleted = service.delete(id_source)

                if not deleted:
                    session.rollback()
                    TrainingSourceMenu.display_error("Training source not found.")
                    return

                session.commit()
                TrainingSourceMenu.display_success("Training source deleted.")
            except Exception:
                session.rollback()
                raise