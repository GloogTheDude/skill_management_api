from datetime import date
from decimal import Decimal

from db.repositories.certification_repository import CertificationRepository
from db.repositories.diploma_repository import DiplomaRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_skill_repository import TrainingSkillRepository
from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_dto import TrainingCrudDTO, TrainingSummaryDTO
from models.training import Training
from models.training_skill import TrainingSkill


class TrainingService:
    def __init__(
        self,
        training_repository: TrainingRepository,
        domaine_repository: DomaineRepository | None = None,
        training_source_repository: TrainingSourceRepository | None = None,
        diploma_repository: DiplomaRepository | None = None,
        certification_repository: CertificationRepository | None = None,
        training_skill_repository: TrainingSkillRepository | None = None,
    ):
        self.training_repository = training_repository
        self.domaine_repository = domaine_repository
        self.training_source_repository = training_source_repository
        self.diploma_repository = diploma_repository
        self.certification_repository = certification_repository
        self.training_skill_repository = training_skill_repository

    def fetch_available_training(
        self,
        employee_id: int,
    ) -> dict[int, TrainingSummaryDTO]:
        results = self.training_repository.get_future_trainings(employee_id)
        trainings: dict[int, TrainingSummaryDTO] = {}
        i = 1

        for training, domaine_name in results:
            trainings[i] = TrainingSummaryDTO(
                id_training=training.id_training,
                title=training.title,
                domaine_name=domaine_name,
                start_date=training.start_,
                end_date=training.end_,
            )
            i += 1

        return trainings

    def filter_dto_by_domaine_name(
        self,
        trainings_availables: dict[int, TrainingSummaryDTO],
        domaine_filter: set[str],
    ):
        domaines = set()

        for value in trainings_availables.values():
            domaines.add(value.domaine_name)

        domaines.difference_update(domaine_filter)
        return domaines

    def get_by_id(self, id_training: int) -> Training | None:
        return self.training_repository.get_by_id(id_training)

    def get_all_for_crud(self) -> list[TrainingCrudDTO]:
        rows = self.training_repository.get_all_for_crud()

        return [
            TrainingCrudDTO(
                id_training=id_training,
                title=title,
                domaine_name=domaine_name,
                source_name=source_name,
                certification_name=certification_name,
                diploma_name=diploma_name,
                start_=start_,
                end_=end_,
                cost_hour=cost_hour,
                duration_hours=duration_hours,
            )
            for (
                id_training,
                title,
                domaine_name,
                source_name,
                certification_name,
                diploma_name,
                start_,
                end_,
                cost_hour,
                duration_hours,
            ) in rows
        ]

    def get_training_type(self, id_training: int) -> tuple[str, int] | None:
        training = self.training_repository.get_by_id(id_training)

        if training is None:
            return None

        if training.id_diploma:
            return ("diploma", training.id_diploma)

        if training.id_certification:
            return ("certification", training.id_certification)

        return None

    def create(
        self,
        title: str,
        id_domaine: int,
        id_source: int,
        start_: date,
        end_: date,
        cost_hour: Decimal | None,
        duration_hours: Decimal | None,
        id_diploma: int | None,
        id_certification: int | None,
        skill_levels: list[tuple[int, int]],
    ) -> Training | None:
        if not self._is_valid_training_payload(
            id_domaine,
            id_source,
            id_diploma,
            id_certification,
            skill_levels,
        ):
            return None

        training = Training()
        training.title = title
        training.id_domaine = id_domaine
        training.id_source = id_source
        training.start_ = start_
        training.end_ = end_
        training.cost_hour = cost_hour
        training.duration_hours = duration_hours
        training.id_diploma = id_diploma
        training.id_certification = id_certification
        training.is_deleted = False

        return self.training_repository.add(training)

    def update(
        self,
        id_training: int,
        title: str,
        id_domaine: int,
        id_source: int,
        start_: date,
        end_: date,
        cost_hour: Decimal | None,
        duration_hours: Decimal | None,
        id_diploma: int | None,
        id_certification: int | None,
        skill_levels: list[tuple[int, int]],
    ) -> Training | None:
        training = self.training_repository.get_by_id(id_training)

        if training is None or training.is_deleted:
            return None

        if not self._is_valid_training_payload(
            id_domaine,
            id_source,
            id_diploma,
            id_certification,
            skill_levels,
        ):
            return None

        training.title = title
        training.id_domaine = id_domaine
        training.id_source = id_source
        training.start_ = start_
        training.end_ = end_
        training.cost_hour = cost_hour
        training.duration_hours = duration_hours
        training.id_diploma = id_diploma
        training.id_certification = id_certification

        return training

    def delete(self, id_training: int) -> bool:
        training = self.training_repository.get_by_id(id_training)

        if training is None or training.is_deleted:
            return False

        self.training_repository.soft_delete(training)
        return True

    def replace_skills(
        self,
        id_training: int,
        skill_levels: list[tuple[int, int]],
    ) -> bool:
        if self.training_skill_repository is None:
            raise ValueError("TrainingSkillRepository is required to replace skills.")

        training = self.training_repository.get_by_id(id_training)

        if training is None or training.is_deleted:
            return False

        existing_links = self.training_skill_repository.get_all_by_training_id(
            id_training
        )
        existing_by_skill_id = {
            link.id_skill: link
            for link in existing_links
        }

        selected_skill_ids = set()

        for id_skill, granted_level in skill_levels:
            selected_skill_ids.add(id_skill)

            if id_skill in existing_by_skill_id:
                link = existing_by_skill_id[id_skill]
                link.granted_level = granted_level
                link.is_deleted = False
            else:
                link = TrainingSkill()
                link.id_training = id_training
                link.id_skill = id_skill
                link.granted_level = granted_level
                link.is_deleted = False

                self.training_skill_repository.add(link)

        for link in existing_links:
            if link.id_skill not in selected_skill_ids:
                link.is_deleted = True

        return True

    def _is_valid_training_payload(
        self,
        id_domaine: int,
        id_source: int,
        id_diploma: int | None,
        id_certification: int | None,
        skill_levels: list[tuple[int, int]],
    ) -> bool:
        if id_diploma is not None and id_certification is not None:
            return False

        if id_diploma is None and id_certification is None and not skill_levels:
            return False

        if self.domaine_repository is not None:
            domaine = self.domaine_repository.get_by_id(id_domaine)

            if domaine is None or domaine.is_deleted:
                return False

        if self.training_source_repository is not None:
            source = self.training_source_repository.get_by_id(id_source)

            if source is None or source.is_deleted:
                return False

        if id_diploma is not None and self.diploma_repository is not None:
            diploma = self.diploma_repository.get_by_id(id_diploma)

            if diploma is None or diploma.is_deleted:
                return False

        if id_certification is not None and self.certification_repository is not None:
            certification = self.certification_repository.get_by_id(id_certification)

            if certification is None or certification.is_deleted:
                return False

        return True