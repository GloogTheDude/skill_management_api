from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, event
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from core.constants import PARTICIPATIONSTATUS, TRAININGREQUESTSTATUS
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from models import Base
from models.access_level import AccessLevel
from models.domaine import Domaine
from models.employee import Employee
from models.participation import Participation
from models.role import Role
from models.training import Training
from models.training_request import TrainingRequest
from services.available_training_service import AvailableTrainingService


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    current_session = sessionmaker(bind=engine)()
    today = date.today()
    current_session.add_all(
        [
            AccessLevel(id_access_level=1, label="Employee", level=1),
            Role(id_role=1, denomination_role="Employee", id_access_level=1),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
            Domaine(id_domaine=2, nom_domaine="Database", is_deleted=False),
            Domaine(id_domaine=3, nom_domaine="Archived", is_deleted=True),
            Employee(
                id_employee=1,
                first_name="Ada",
                last_name="Lovelace",
                hash_password="hash",
                mail="ada@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Employee(
                id_employee=2,
                first_name="Deleted",
                last_name="Employee",
                hash_password="hash",
                mail="deleted@example.com",
                id_role=1,
                is_deleted=True,
            ),
        ]
    )
    current_session.add_all(
        [
            Training(id_training=1, title="Available", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=2, title="Pending request", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=3, title="Validated request", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=4, title="Refused request", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=5, title="Cancelled request", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=6, title="Deleted request", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=7, title="Registered", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=8, title="In progress", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=9, title="Completed", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=10, title="Failed", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=11, title="Absent", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=12, title="Cancelled", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=13, title="Deleted participation", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=14, title="Past", id_domaine=1, start_=today - timedelta(days=1), end_=today + timedelta(days=1), is_deleted=False),
            Training(id_training=15, title="Today", id_domaine=1, start_=today, end_=today + timedelta(days=1), is_deleted=False),
            Training(id_training=16, title="No start", id_domaine=1, start_=None, end_=today + timedelta(days=1), is_deleted=False),
            Training(id_training=17, title="No end", id_domaine=1, start_=today + timedelta(days=1), end_=None, is_deleted=False),
            Training(id_training=18, title="Deleted training", id_domaine=1, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=True),
            Training(id_training=19, title="Deleted domain", id_domaine=3, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=20, title="Other domain", id_domaine=2, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
            Training(id_training=21, title="No domain", id_domaine=None, start_=today + timedelta(days=1), end_=today + timedelta(days=2), is_deleted=False),
        ]
    )
    current_session.add_all(
        [
            TrainingRequest(id_training_request=1, id_employee=1, id_training=2, status=TRAININGREQUESTSTATUS.PENDING.value, requested_at=today, is_deleted=False),
            TrainingRequest(id_training_request=2, id_employee=1, id_training=3, status=TRAININGREQUESTSTATUS.VALIDATED.value, requested_at=today, is_deleted=False),
            TrainingRequest(id_training_request=3, id_employee=1, id_training=4, status=TRAININGREQUESTSTATUS.REFUSED.value, requested_at=today, is_deleted=False),
            TrainingRequest(id_training_request=4, id_employee=1, id_training=5, status="CANCELLED", requested_at=today, is_deleted=False),
            TrainingRequest(id_training_request=5, id_employee=1, id_training=6, status=TRAININGREQUESTSTATUS.REFUSED.value, requested_at=today, is_deleted=True),
            Participation(id_employee=1, id_training=7, status=PARTICIPATIONSTATUS.REGISTERED.value, is_deleted=False),
            Participation(id_employee=1, id_training=8, status=PARTICIPATIONSTATUS.IN_PROGRESS.value, is_deleted=False),
            Participation(id_employee=1, id_training=9, status=PARTICIPATIONSTATUS.COMPLETED.value, is_deleted=False),
            Participation(id_employee=1, id_training=10, status=PARTICIPATIONSTATUS.FAILED.value, is_deleted=False),
            Participation(id_employee=1, id_training=11, status=PARTICIPATIONSTATUS.ABSENT.value, is_deleted=False),
            Participation(id_employee=1, id_training=12, status=PARTICIPATIONSTATUS.CANCELLED.value, is_deleted=False),
            Participation(id_employee=1, id_training=13, status=PARTICIPATIONSTATUS.COMPLETED.value, is_deleted=True),
        ]
    )
    current_session.commit()
    yield current_session
    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def service(session):
    return AvailableTrainingService(EmployeeRepository(session), TrainingRepository(session))


def test_available_trainings_apply_dates_and_soft_deletes(session):
    result = service(session).get_available_trainings(1)

    assert [training.id_training for training in result] == [1, 17, 20]


@pytest.mark.parametrize("training_id", [2, 3, 4, 5, 6])
def test_any_training_request_blocks_availability(session, training_id):
    result = service(session).get_available_trainings(1)

    assert training_id not in {training.id_training for training in result}


@pytest.mark.parametrize("training_id", [7, 8, 9, 10, 11, 12, 13])
def test_any_participation_blocks_availability_even_soft_deleted(session, training_id):
    result = service(session).get_available_trainings(1)

    assert training_id not in {training.id_training for training in result}


def test_domain_filter_is_optional_and_applied_in_sql(session):
    assert [item.id_training for item in service(session).get_available_trainings(1, 1)] == [1, 17]
    assert [item.id_training for item in service(session).get_available_trainings(1, 2)] == [20]
    assert service(session).get_available_trainings(1, 3) == []


def test_missing_or_deleted_employee_is_not_available(session):
    with pytest.raises(NoResultFound):
        service(session).get_available_trainings(999)
    with pytest.raises(NoResultFound):
        service(session).get_available_trainings(2)


def test_query_count_does_not_depend_on_training_count(session):
    statements = []

    @event.listens_for(session.bind, "before_cursor_execute")
    def count_statements(*args):
        statements.append(args[2])

    service(session).get_available_trainings(1)

    assert len(statements) == 2
