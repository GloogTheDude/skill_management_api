from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, event
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

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
from models import Base
from models.access_level import AccessLevel
from models.certification import Certification
from models.diploma import Diploma
from models.domaine import Domaine
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.participation import Participation
from models.role import Role
from models.training import Training
from models.training_source import TrainingSource
from services.participation_completion_service import ParticipationCompletionService
from services.participation_service import ParticipationService


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    current_session = session_factory()
    current_session.add_all(
        [
            AccessLevel(id_access_level=1, label="Employee", level=1),
            Role(
                id_role=1,
                denomination_role="Developer",
                id_access_level=1,
                is_deleted=False,
            ),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
            TrainingSource(
                id_source=1,
                name_source="Training provider",
                is_deleted=False,
            ),
            Employee(
                id_employee=1,
                first_name="Ada",
                last_name="Lovelace",
                hash_password="hash",
                mail="ada@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Diploma(
                id_diploma=1,
                subject_diploma="Computer Science",
                level_diploma="Bachelor",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=1,
                subject_certification="Python",
                validity_month=12,
                id_domaine=1,
                is_deleted=False,
            ),
        ]
    )
    current_session.commit()

    yield current_session

    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def completion_service(session):
    return ParticipationCompletionService(
        ParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
    )


def add_training_and_participation(
    session,
    *,
    training_id,
    status=PARTICIPATIONSTATUS.IN_PROGRESS.value,
    id_diploma=None,
    id_certification=None,
    end_=None,
    is_deleted=False,
    participation_is_deleted=False,
):
    training = Training(
        id_training=training_id,
        title=f"Training {training_id}",
        id_domaine=1,
        id_source=1,
        id_diploma=id_diploma,
        id_certification=id_certification,
        start_=date.today() - timedelta(days=10),
        end_=end_,
        is_deleted=is_deleted,
    )
    participation = Participation(
        id_employee=1,
        id_training=training_id,
        status=status,
        is_deleted=participation_is_deleted,
    )
    session.add_all([training, participation])
    session.commit()


def test_get_all_and_get_by_id_exclude_soft_deleted(session):
    add_training_and_participation(session, training_id=1, end_=date.today())
    session.add(
        Training(
            id_training=2,
            title="Deleted training",
            id_domaine=1,
            id_source=1,
            start_=date.today(),
            end_=date.today(),
            is_deleted=True,
        )
    )
    session.add(
        Participation(
            id_employee=1,
            id_training=2,
            status=PARTICIPATIONSTATUS.REGISTERED.value,
            is_deleted=True,
        )
    )
    session.commit()

    service = ParticipationService(ParticipationRepository(session))

    assert len(service.get_all()) == 1
    with pytest.raises(NoResultFound):
        service.get_by_id(1, 2)


@pytest.mark.parametrize(
    "status",
    [
        PARTICIPATIONSTATUS.REGISTERED.value,
        PARTICIPATIONSTATUS.COMPLETED.value,
        PARTICIPATIONSTATUS.FAILED.value,
    ],
)
def test_complete_rejects_status_other_than_in_progress(session, status):
    add_training_and_participation(
        session,
        training_id=1,
        status=status,
        id_diploma=1,
        end_=date.today(),
    )

    with pytest.raises(ParticipationInvalidStatus):
        completion_service(session).complete(1, 1)


def test_complete_rejects_missing_or_deleted_participation(session):
    with pytest.raises(NoResultFound):
        completion_service(session).complete(1, 1)

    add_training_and_participation(session, training_id=2, end_=date.today())
    participation = session.query(Participation).filter_by(
        id_employee=1,
        id_training=2,
    ).one()
    participation.is_deleted = True
    session.commit()

    with pytest.raises(NoResultFound):
        completion_service(session).complete(1, 2)


def test_complete_rejects_deleted_training(session):
    add_training_and_participation(
        session,
        training_id=1,
        end_=date.today(),
        is_deleted=True,
    )

    with pytest.raises(NoResultFound):
        completion_service(session).complete(1, 1)


@pytest.mark.parametrize(
    "end_",
    [None, date.today() + timedelta(days=1)],
)
def test_complete_rejects_training_not_finished(session, end_):
    add_training_and_participation(
        session,
        training_id=1,
        id_diploma=1,
        end_=end_,
    )

    with pytest.raises(TrainingNotCompleted):
        completion_service(session).complete(1, 1)


def test_complete_diploma_training_creates_diploma_and_completes(session):
    add_training_and_participation(
        session,
        training_id=1,
        id_diploma=1,
        end_=date.today(),
    )

    completed = completion_service(session).complete(1, 1)
    session.commit()

    diploma = session.query(EmployeeDiploma).one()
    assert completed.status == PARTICIPATIONSTATUS.COMPLETED.value
    assert diploma.id_employee == 1
    assert diploma.id_diploma == 1
    assert diploma.distinction is None
    assert diploma.school == "Training provider"


def test_complete_certification_training_calculates_expiration(session):
    add_training_and_participation(
        session,
        training_id=1,
        id_certification=1,
        end_=date.today(),
    )

    completed = completion_service(session).complete(1, 1)
    session.commit()

    certification = session.query(EmployeeCertification).one()
    assert completed.status == PARTICIPATIONSTATUS.COMPLETED.value
    assert certification.id_employee == 1
    assert certification.id_certification == 1
    assert certification.expiration == date.today() + relativedelta(months=12)


def test_complete_skill_training_creates_no_secondary_qualification(session):
    add_training_and_participation(session, training_id=1, end_=date.today())

    completed = completion_service(session).complete(1, 1)
    session.commit()

    assert completed.status == PARTICIPATIONSTATUS.COMPLETED.value
    assert session.query(EmployeeDiploma).count() == 0
    assert session.query(EmployeeCertification).count() == 0


def test_complete_rolls_back_secondary_creation_when_status_update_fails(session):
    add_training_and_participation(
        session,
        training_id=1,
        id_diploma=1,
        end_=date.today(),
    )

    class FailingParticipationRepository(ParticipationRepository):
        def update_status(self, id_employee, id_training, status):
            raise RuntimeError("status update failed")

    service = ParticipationCompletionService(
        FailingParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
    )

    with pytest.raises(RuntimeError):
        service.complete(1, 1)
    session.rollback()

    assert session.query(EmployeeDiploma).count() == 0
    assert session.query(Participation).one().status == (
        PARTICIPATIONSTATUS.IN_PROGRESS.value
    )


def test_get_completable_filters_status_and_dates(session):
    add_training_and_participation(session, training_id=1, end_=date.today())
    add_training_and_participation(
        session,
        training_id=2,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        end_=date.today(),
    )
    add_training_and_participation(
        session,
        training_id=3,
        end_=date.today() + timedelta(days=1),
    )
    add_training_and_participation(
        session,
        training_id=4,
        end_=date.today(),
        is_deleted=True,
    )
    add_training_and_participation(
        session,
        training_id=5,
        end_=date.today(),
        participation_is_deleted=True,
    )

    result = ParticipationService(
        ParticipationRepository(session)
    ).get_completable()

    assert len(result) == 1
    assert result[0].id_training == 1
