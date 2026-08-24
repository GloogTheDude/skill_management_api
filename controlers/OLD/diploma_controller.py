from core.database import SessionLocal
from db.repositories.diploma_repository import DiplomaRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.diploma_skill_repository import DiplomaSkillRepository
from menus.diploma_menu import DiplomaMenu
from menus.skill_link_menu import SkillLinkMenu
from services.diploma_service import DiplomaService


class DiplomaController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = DiplomaMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_diplomas()
                case 2:
                    self.create_diploma()
                case 3:
                    self.update_diploma()
                case 4:
                    self.delete_diploma()
                case 0:
                    return

    def list_diplomas(self) -> None:
        with SessionLocal() as session:
            repo = DiplomaRepository(session)
            service = DiplomaService(repo)

            diplomas = service.get_all_for_crud()

        DiplomaMenu.display_diplomas(diplomas)

    def create_diploma(self) -> None:
        subject_diploma = DiplomaMenu.ask_subject_diploma()
        level_diploma = DiplomaMenu.ask_level_diploma()
        id_domaine = DiplomaMenu.ask_id_domaine()
        skill_levels = SkillLinkMenu.ask_skill_levels()

        if not subject_diploma or not level_diploma:
            DiplomaMenu.display_error("Subject and level cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                diploma_repo = DiplomaRepository(session)
                domaine_repo = DomaineRepository(session)
                diploma_skill_repo = DiplomaSkillRepository(session)

                service = DiplomaService(
                    diploma_repo,
                    domaine_repo,
                    diploma_skill_repo,
                )

                created = service.create(
                    subject_diploma,
                    level_diploma,
                    id_domaine,
                )

                if created is None:
                    session.rollback()
                    DiplomaMenu.display_error("Invalid domaine.")
                    return

                session.flush()

                service.replace_skills(
                    created.id_diploma,
                    skill_levels,
                )

                session.commit()
                DiplomaMenu.display_success("Diploma created.")
            except Exception:
                session.rollback()
                raise

    def update_diploma(self) -> None:
        id_diploma = DiplomaMenu.ask_id_diploma()
        subject_diploma = DiplomaMenu.ask_subject_diploma()
        level_diploma = DiplomaMenu.ask_level_diploma()
        id_domaine = DiplomaMenu.ask_id_domaine()
        skill_levels = SkillLinkMenu.ask_skill_levels()

        if not subject_diploma or not level_diploma:
            DiplomaMenu.display_error("Subject and level cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                diploma_repo = DiplomaRepository(session)
                domaine_repo = DomaineRepository(session)
                diploma_skill_repo = DiplomaSkillRepository(session)

                service = DiplomaService(
                    diploma_repo,
                    domaine_repo,
                    diploma_skill_repo,
                )

                updated = service.update(
                    id_diploma,
                    subject_diploma,
                    level_diploma,
                    id_domaine,
                )

                if updated is None:
                    session.rollback()
                    DiplomaMenu.display_error(
                        "Diploma not found or invalid domaine."
                    )
                    return

                service.replace_skills(
                    id_diploma,
                    skill_levels,
                )

                session.commit()
                DiplomaMenu.display_success("Diploma updated.")
            except Exception:
                session.rollback()
                raise

    def delete_diploma(self) -> None:
        id_diploma = DiplomaMenu.ask_id_diploma()

        with SessionLocal() as session:
            try:
                repo = DiplomaRepository(session)
                service = DiplomaService(repo)

                deleted = service.delete(id_diploma)

                if not deleted:
                    session.rollback()
                    DiplomaMenu.display_error("Diploma not found.")
                    return

                session.commit()
                DiplomaMenu.display_success("Diploma deleted.")
            except Exception:
                session.rollback()
                raise