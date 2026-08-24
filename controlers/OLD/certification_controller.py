from core.database import SessionLocal
from db.repositories.certification_repository import CertificationRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.certification_skill_repository import CertificationSkillRepository
from menus.certification_menu import CertificationMenu
from menus.skill_link_menu import SkillLinkMenu
from services.certification_service import CertificationService


class CertificationController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = CertificationMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_certifications()
                case 2:
                    self.create_certification()
                case 3:
                    self.update_certification()
                case 4:
                    self.delete_certification()
                case 0:
                    return

    def list_certifications(self) -> None:
        with SessionLocal() as session:
            repo = CertificationRepository(session)
            service = CertificationService(repo)

            certifications = service.get_all_for_crud()

        CertificationMenu.display_certifications(certifications)

    def create_certification(self) -> None:
        subject_certification = CertificationMenu.ask_subject_certification()
        validity_month = CertificationMenu.ask_validity_month()
        id_domaine = CertificationMenu.ask_id_domaine()
        skill_levels = SkillLinkMenu.ask_skill_levels()

        if not subject_certification:
            CertificationMenu.display_error("Subject cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                certification_repo = CertificationRepository(session)
                domaine_repo = DomaineRepository(session)
                certification_skill_repo = CertificationSkillRepository(session)

                service = CertificationService(
                    certification_repo,
                    domaine_repo,
                    certification_skill_repo,
                )

                created = service.create(
                    subject_certification,
                    validity_month,
                    id_domaine,
                )

                if created is None:
                    session.rollback()
                    CertificationMenu.display_error("Invalid domaine.")
                    return

                session.flush()

                service.replace_skills(
                    created.id_certification,
                    skill_levels,
                )

                session.commit()
                CertificationMenu.display_success("Certification created.")
            except Exception:
                session.rollback()
                raise

    def update_certification(self) -> None:
        id_certification = CertificationMenu.ask_id_certification()
        subject_certification = CertificationMenu.ask_subject_certification()
        validity_month = CertificationMenu.ask_validity_month()
        id_domaine = CertificationMenu.ask_id_domaine()
        skill_levels = SkillLinkMenu.ask_skill_levels()

        if not subject_certification:
            CertificationMenu.display_error("Subject cannot be empty.")
            return

        with SessionLocal() as session:
            try:
                certification_repo = CertificationRepository(session)
                domaine_repo = DomaineRepository(session)
                certification_skill_repo = CertificationSkillRepository(session)

                service = CertificationService(
                    certification_repo,
                    domaine_repo,
                    certification_skill_repo,
                )

                updated = service.update(
                    id_certification,
                    subject_certification,
                    validity_month,
                    id_domaine,
                )

                if updated is None:
                    session.rollback()
                    CertificationMenu.display_error(
                        "Certification not found or invalid domaine."
                    )
                    return

                service.replace_skills(
                    id_certification,
                    skill_levels,
                )

                session.commit()
                CertificationMenu.display_success("Certification updated.")
            except Exception:
                session.rollback()
                raise

    def delete_certification(self) -> None:
        id_certification = CertificationMenu.ask_id_certification()

        with SessionLocal() as session:
            try:
                repo = CertificationRepository(session)
                service = CertificationService(repo)

                deleted = service.delete(id_certification)

                if not deleted:
                    session.rollback()
                    CertificationMenu.display_error("Certification not found.")
                    return

                session.commit()
                CertificationMenu.display_success("Certification deleted.")
            except Exception:
                session.rollback()
                raise