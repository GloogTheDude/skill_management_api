from datetime import date

from sqlalchemy import exists, select

from db.repositories.base_repository import BaseRepository
from models.domaine import Domaine
from models.participation import Participation
from models.training import Training
from models.training_request import TrainingRequest


class TrainingRepository(BaseRepository[Training]):
    model = Training

    @staticmethod
    def _availability_conditions(id_employee: int):
        request_exists = exists(
            select(1).where(
                TrainingRequest.id_employee == id_employee,
                TrainingRequest.id_training == Training.id_training,
            )
        )
        participation_exists = exists(
            select(1).where(
                Participation.id_employee == id_employee,
                Participation.id_training == Training.id_training,
            )
        )
        return (
            Training.start_ > date.today(),
            Training.is_deleted.is_(False),
            Domaine.is_deleted.is_(False),
            ~request_exists,
            ~participation_exists,
        )

    def get_available_for_employee(
        self,
        id_employee: int,
        id_domaine: int | None = None,
    ) -> list[tuple[Training, str]]:
        stmt = (
            select(Training, Domaine.nom_domaine)
            .join(Domaine, Training.id_domaine == Domaine.id_domaine)
            .where(*self._availability_conditions(id_employee))
            .order_by(Training.id_training)
        )
        if id_domaine is not None:
            stmt = stmt.where(Training.id_domaine == id_domaine)

        return list(self._session.execute(stmt).all())

    def is_available_for_employee(self, id_employee: int, id_training: int) -> bool:
        stmt = (
            select(Training.id_training)
            .join(Domaine, Training.id_domaine == Domaine.id_domaine)
            .where(
                Training.id_training == id_training,
                *self._availability_conditions(id_employee),
            )
        )
        return self._session.scalar(stmt) is not None
