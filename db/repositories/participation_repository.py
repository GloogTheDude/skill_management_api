from datetime import date

from sqlalchemy import select

from core.constants import PARTICIPATIONSTATUS
from db.repositories.base_repository import BaseRepository
from models.employee import Employee
from models.participation import Participation
from models.training import Training


class ParticipationRepository(BaseRepository[Participation]):
    model = Participation

    def get_completable(
        self,
    ) -> list[tuple[Participation, Employee, Training]]:
        stmt = (
            select(Participation, Employee, Training)
            .join(Employee, Employee.id_employee == Participation.id_employee)
            .join(Training, Training.id_training == Participation.id_training)
            .where(
                Participation.status == PARTICIPATIONSTATUS.IN_PROGRESS.value,
                Participation.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
                Training.is_deleted.is_(False),
                Training.end_.is_not(None),
                Training.end_ <= date.today(),
            )
        )
        return list(self._session.execute(stmt).all())

    def update_status(
        self,
        id_employee: int,
        id_training: int,
        status: str,
    ) -> Participation:
        participation = self.get_one((id_employee, id_training))
        participation.status = status
        self._session.flush()
        return participation
