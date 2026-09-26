from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import NoResultFound

from core.constants import PARTICIPATIONSTATUS
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from errors.participation_errors import (
    ParticipationInvalidStatus,
    TrainingNotCompleted,
)
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.participation import Participation


class ParticipationCompletionService:
    def __init__(
        self,
        participation_repository: ParticipationRepository,
        training_repository: TrainingRepository,
        employee_diploma_repository: EmployeeDiplomaRepository,
        employee_certification_repository: EmployeeCertificationRepository,
    ):
        self.participation_repository = participation_repository
        self.training_repository = training_repository
        self.employee_diploma_repository = employee_diploma_repository
        self.employee_certification_repository = employee_certification_repository

    def complete(
        self,
        id_employee: int,
        id_training: int,
    ) -> Participation:
        participation = self.participation_repository.get_one(
            (id_employee, id_training)
        )
        if participation.is_deleted:
            raise NoResultFound()

        if participation.status != PARTICIPATIONSTATUS.IN_PROGRESS.value:
            raise ParticipationInvalidStatus(participation.status)

        training = self.training_repository.get_one(id_training)
        if training.is_deleted:
            raise NoResultFound()

        if training.end_ is None or training.end_ > date.today():
            raise TrainingNotCompleted()

        source_name = (
            training.source.name_source
            if training.source is not None
            else None
        )

        if training.id_diploma:
            employee_diploma = EmployeeDiploma(
                id_employee=id_employee,
                id_diploma=training.id_diploma,
                start_=training.start_,
                end_=training.end_,
                school=source_name,
                distinction=None,
                doc=None,
                is_deleted=False,
            )
            self.employee_diploma_repository.add(employee_diploma)
        elif training.id_certification:
            certification = training.certification
            expiration = None
            if certification.validity_month is not None and training.end_ is not None:
                expiration = training.end_ + relativedelta(
                    months=certification.validity_month
                )

            employee_certification = EmployeeCertification(
                id_employee=id_employee,
                id_certification=training.id_certification,
                start_=training.start_,
                end_=training.end_,
                expiration=expiration,
                organism=source_name,
                evaluation=None,
                doc=None,
                is_deleted=False,
            )
            self.employee_certification_repository.add(employee_certification)

        return self.participation_repository.update_status(
            id_employee,
            id_training,
            PARTICIPATIONSTATUS.COMPLETED.value,
        )
