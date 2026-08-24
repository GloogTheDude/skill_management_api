from core.database import SessionLocal
from db.repositories.skills_repository import SkillRepository
from menus.skill_menu import SkillMenu
from services.skill_service import SkillService


class SkillController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = SkillMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_skills()
                case 2:
                    self.create_skill()
                case 3:
                    self.update_skill()
                case 4:
                    self.delete_skill()
                case 0:
                    return

    def list_skills(self) -> None:
        with SessionLocal() as session:
            repo = SkillRepository(session)
            service = SkillService(repo)

            skills = service.get_all_for_crud()

        SkillMenu.display_skills(skills)

    def create_skill(self) -> None:
        name_skill = SkillMenu.ask_name_skill()
        id_domaine = SkillMenu.ask_id_domaine()

        if not name_skill:
            SkillMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = SkillRepository(session)
                service = SkillService(repo)

                service.create(name_skill, id_domaine)

                session.commit()
                SkillMenu.display_success("Skill created.")
            except Exception:
                session.rollback()
                raise

    def update_skill(self) -> None:
        id_skill = SkillMenu.ask_id_skill()
        name_skill = SkillMenu.ask_name_skill()
        id_domaine = SkillMenu.ask_id_domaine()

        if not name_skill:
            SkillMenu.display_error("Name cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                repo = SkillRepository(session)
                service = SkillService(repo)

                updated = service.update(id_skill, name_skill, id_domaine)

                if updated is None:
                    session.rollback()
                    SkillMenu.display_error("Skill not found.")
                    return

                session.commit()
                SkillMenu.display_success("Skill updated.")
            except Exception:
                session.rollback()
                raise

    def delete_skill(self) -> None:
        id_skill = SkillMenu.ask_id_skill()

        with SessionLocal() as session:
            try:
                repo = SkillRepository(session)
                service = SkillService(repo)

                deleted = service.delete(id_skill)

                if not deleted:
                    session.rollback()
                    SkillMenu.display_error("Skill not found.")
                    return

                session.commit()
                SkillMenu.display_success("Skill deleted.")
            except Exception:
                session.rollback()
                raise