from core.database import SessionLocal
from db.repositories.certification_repository import CertificationRepository
from db.repositories.diploma_repository import DiplomaRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_skill_repository import TrainingSkillRepository
from db.repositories.training_source_repository import TrainingSourceRepository
from menus.skill_link_menu import SkillLinkMenu
from menus.training_menu import TrainingMenu
from services.training_service import TrainingService


class TrainingController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = TrainingMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_trainings()
                case 2:
                    self.create_training()
                case 3:
                    self.update_training()
                case 4:
                    self.delete_training()
                case 0:
                    return

    def list_trainings(self) -> None:
        with SessionLocal() as session:
            repo = TrainingRepository(session)
            service = TrainingService(repo)
            trainings = service.get_all_for_crud()

        TrainingMenu.display_trainings(trainings)

    def create_training(self) -> None:
        title = TrainingMenu.ask_title()
        id_domaine = TrainingMenu.ask_id_domaine()
        id_source = TrainingMenu.ask_id_source()
        start_ = TrainingMenu.ask_date("Start")
        end_ = TrainingMenu.ask_date("End")
        cost_hour = TrainingMenu.ask_decimal("Cost/hour")
        duration_hours = TrainingMenu.ask_decimal("Duration hours")
        id_diploma = TrainingMenu.ask_optional_id("Diploma id")
        id_certification = TrainingMenu.ask_optional_id("Certification id")

        skill_levels = []

        if id_diploma is None and id_certification is None:
            skill_levels = SkillLinkMenu.ask_skill_levels()

        if not title:
            TrainingMenu.display_error("Title cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                training_repo = TrainingRepository(session)
                domaine_repo = DomaineRepository(session)
                source_repo = TrainingSourceRepository(session)
                diploma_repo = DiplomaRepository(session)
                certification_repo = CertificationRepository(session)
                training_skill_repo = TrainingSkillRepository(session)

                service = TrainingService(
                    training_repo,
                    domaine_repo,
                    source_repo,
                    diploma_repo,
                    certification_repo,
                    training_skill_repo,
                )

                created = service.create(
                    title=title,
                    id_domaine=id_domaine,
                    id_source=id_source,
                    start_=start_,
                    end_=end_,
                    cost_hour=cost_hour,
                    duration_hours=duration_hours,
                    id_diploma=id_diploma,
                    id_certification=id_certification,
                    skill_levels=skill_levels,
                )

                if created is None:
                    session.rollback()
                    TrainingMenu.display_error(
                        "Invalid training data. Check domain, source, target and skills."
                    )
                    return

                session.flush()

                if id_diploma is None and id_certification is None:
                    service.replace_skills(
                        created.id_training,
                        skill_levels,
                    )

                session.commit()
                TrainingMenu.display_success("Training created.")
            except Exception:
                session.rollback()
                raise

    def update_training(self) -> None:
        id_training = TrainingMenu.ask_id_training()
        title = TrainingMenu.ask_title()
        id_domaine = TrainingMenu.ask_id_domaine()
        id_source = TrainingMenu.ask_id_source()
        start_ = TrainingMenu.ask_date("Start")
        end_ = TrainingMenu.ask_date("End")
        cost_hour = TrainingMenu.ask_decimal("Cost/hour")
        duration_hours = TrainingMenu.ask_decimal("Duration hours")
        id_diploma = TrainingMenu.ask_optional_id("Diploma id")
        id_certification = TrainingMenu.ask_optional_id("Certification id")

        skill_levels = []

        if id_diploma is None and id_certification is None:
            skill_levels = SkillLinkMenu.ask_skill_levels()

        if not title:
            TrainingMenu.display_error("Title cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                training_repo = TrainingRepository(session)
                domaine_repo = DomaineRepository(session)
                source_repo = TrainingSourceRepository(session)
                diploma_repo = DiplomaRepository(session)
                certification_repo = CertificationRepository(session)
                training_skill_repo = TrainingSkillRepository(session)

                service = TrainingService(
                    training_repo,
                    domaine_repo,
                    source_repo,
                    diploma_repo,
                    certification_repo,
                    training_skill_repo,
                )

                updated = service.update(
                    id_training=id_training,
                    title=title,
                    id_domaine=id_domaine,
                    id_source=id_source,
                    start_=start_,
                    end_=end_,
                    cost_hour=cost_hour,
                    duration_hours=duration_hours,
                    id_diploma=id_diploma,
                    id_certification=id_certification,
                    skill_levels=skill_levels,
                )

                if updated is None:
                    session.rollback()
                    TrainingMenu.display_error(
                        "Training not found or invalid training data."
                    )
                    return

                if id_diploma is None and id_certification is None:
                    service.replace_skills(
                        id_training,
                        skill_levels,
                    )
                else:
                    service.replace_skills(
                        id_training,
                        [],
                    )

                session.commit()
                TrainingMenu.display_success("Training updated.")
            except Exception:
                session.rollback()
                raise

    def delete_training(self) -> None:
        id_training = TrainingMenu.ask_id_training()

        with SessionLocal() as session:
            try:
                repo = TrainingRepository(session)
                service = TrainingService(repo)

                deleted = service.delete(id_training)

                if not deleted:
                    session.rollback()
                    TrainingMenu.display_error("Training not found.")
                    return

                session.commit()
                TrainingMenu.display_success("Training deleted.")
            except Exception:
                session.rollback()
                raise