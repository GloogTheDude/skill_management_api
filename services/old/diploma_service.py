from db.repositories.diploma_repository import DiplomaRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.diploma_skill_repository import DiplomaSkillRepository
from dto.diploma_dto import DiplomaCrudDTO
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill


class DiplomaService:
    def __init__(
        self,
        diploma_repository: DiplomaRepository,
        domaine_repository: DomaineRepository | None = None,
        diploma_skill_repository: DiplomaSkillRepository | None = None,
    ):
        self.diploma_repository = diploma_repository
        self.domaine_repository = domaine_repository
        self.diploma_skill_repository = diploma_skill_repository

    def get_all(self) -> list[Diploma]:
        return self.diploma_repository.get_all()

    def get_by_id(self, id_diploma: int) -> Diploma | None:
        return self.diploma_repository.get_by_id(id_diploma)

    def get_all_for_crud(self) -> list[DiplomaCrudDTO]:
        rows = self.diploma_repository.get_all_for_crud()

        return [
            DiplomaCrudDTO(
                id_diploma=id_diploma,
                subject_diploma=subject_diploma,
                level_diploma=level_diploma,
                id_domaine=id_domaine,
                domaine_name=domaine_name,
            )
            for id_diploma, subject_diploma, level_diploma, id_domaine, domaine_name in rows
        ]

    def create(
        self,
        subject_diploma: str,
        level_diploma: str,
        id_domaine: int,
    ) -> Diploma | None:
        if self.domaine_repository is not None:
            domaine = self.domaine_repository.get_by_id(id_domaine)

            if domaine is None or domaine.is_deleted:
                return None

        diploma = Diploma()
        diploma.subject_diploma = subject_diploma
        diploma.level_diploma = level_diploma
        diploma.id_domaine = id_domaine
        diploma.is_deleted = False

        return self.diploma_repository.add(diploma)

    def update(
        self,
        id_diploma: int,
        subject_diploma: str,
        level_diploma: str,
        id_domaine: int,
    ) -> Diploma | None:
        diploma = self.diploma_repository.get_by_id(id_diploma)

        if diploma is None or diploma.is_deleted:
            return None

        if self.domaine_repository is not None:
            domaine = self.domaine_repository.get_by_id(id_domaine)

            if domaine is None or domaine.is_deleted:
                return None

        diploma.subject_diploma = subject_diploma
        diploma.level_diploma = level_diploma
        diploma.id_domaine = id_domaine

        return diploma

    def delete(self, id_diploma: int) -> bool:
        diploma = self.diploma_repository.get_by_id(id_diploma)

        if diploma is None or diploma.is_deleted:
            return False

        self.diploma_repository.soft_delete(diploma)
        return True

    def replace_skills(
        self,
        id_diploma: int,
        skill_levels: list[tuple[int, int]],
    ) -> bool:
        if self.diploma_skill_repository is None:
            raise ValueError("DiplomaSkillRepository is required to replace skills.")

        diploma = self.diploma_repository.get_by_id(id_diploma)

        if diploma is None or diploma.is_deleted:
            return False

        existing_links = self.diploma_skill_repository.get_all_by_diploma_id(id_diploma)
        existing_by_skill_id = {
            link.id_skill: link
            for link in existing_links
        }

        selected_skill_ids = set()

        for id_skill, min_level in skill_levels:
            selected_skill_ids.add(id_skill)

            if id_skill in existing_by_skill_id:
                link = existing_by_skill_id[id_skill]
                link.min_level = min_level
                link.is_deleted = False
            else:
                link = DiplomaSkill()
                link.id_diploma = id_diploma
                link.id_skill = id_skill
                link.min_level = min_level
                link.is_deleted = False

                self.diploma_skill_repository.add(link)

        for link in existing_links:
            if link.id_skill not in selected_skill_ids:
                link.is_deleted = True

        return True