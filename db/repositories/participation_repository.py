from datetime import date

from sqlalchemy import exists, select, update

from core.constants import PARTICIPATIONSTATUS
from db.repositories.base_repository import BaseRepository
from models.employee import Employee
from models.participation import Participation
from models.training import Training
from models.domaine import Domaine
from models.training_source import TrainingSource
from core.constants import PermissionProfile, coerce_permission_profile


class ParticipationRepository(BaseRepository[Participation]):
    model = Participation

    def synchronize_started(self, employee_id=None, permission_profile=None) -> None:
        training_started = exists(
            select(1).where(
                Training.id_training == Participation.id_training,
                Training.start_.is_not(None),
                Training.start_ <= date.today(),
                Training.is_deleted.is_(False),
            )
        )
        stmt = update(Participation).where(
            Participation.status == PARTICIPATIONSTATUS.REGISTERED.value,
            Participation.is_deleted.is_(False),
            training_started,
        )
        if employee_id is not None and permission_profile is not None:
            permission_profile = coerce_permission_profile(permission_profile)
            if permission_profile == PermissionProfile.EMPLOYEE:
                stmt = stmt.where(Participation.id_employee == employee_id)
            elif permission_profile == PermissionProfile.MANAGER:
                stmt = stmt.where(
                    exists(select(1).where(
                        Employee.id_employee == Participation.id_employee,
                        (Employee.id_employee == employee_id) | (Employee.id_manager == employee_id),
                    ))
                )
        self._session.execute(stmt.values(status=PARTICIPATIONSTATUS.IN_PROGRESS.value))
        self._session.flush()

    def get_for_scope(self, employee_id: int, permission_profile):
        self.synchronize_started(employee_id, permission_profile)
        permission_profile = coerce_permission_profile(permission_profile)
        stmt = select(
            Participation,
            Employee.first_name,
            Employee.last_name,
            Training.title,
            Domaine.nom_domaine,
            TrainingSource.name_source,
            Training.location,
            Training.start_,
            Training.end_,
            Training.duration_hours,
            Training.cost_hour,
        ).join(Employee, Employee.id_employee == Participation.id_employee)
        stmt = stmt.join(Training, Training.id_training == Participation.id_training)
        stmt = stmt.outerjoin(Domaine, Domaine.id_domaine == Training.id_domaine)
        stmt = stmt.outerjoin(TrainingSource, TrainingSource.id_source == Training.id_source)
        if permission_profile != PermissionProfile.HR:
            if permission_profile == PermissionProfile.EMPLOYEE:
                stmt = stmt.where(Participation.id_employee == employee_id)
            else:
                stmt = stmt.where(
                    (Participation.id_employee == employee_id)
                    | (Employee.id_manager == employee_id)
                )
        stmt = stmt.where(
            Participation.is_deleted.is_(False),
            Employee.is_deleted.is_(False),
        )
        return list(self._session.execute(stmt).all())

    def get_existing(
        self,
        id_employee: int,
        id_training: int,
    ) -> Participation | None:
        return self._session.get(
            Participation,
            (id_employee, id_training),
        )

    def get_completable(
        self,
    ) -> list[tuple[Participation, Employee, Training]]:
        self.synchronize_started()
        stmt = (
            select(Participation, Employee, Training)
            .join(Employee, Employee.id_employee == Participation.id_employee)
            .join(Training, Training.id_training == Participation.id_training)
            .where(
                Participation.status.in_((
                    PARTICIPATIONSTATUS.REGISTERED.value,
                    PARTICIPATIONSTATUS.IN_PROGRESS.value,
                )),
                Participation.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
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
