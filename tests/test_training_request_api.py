from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from core.constants import PARTICIPATIONSTATUS, TRAININGREQUESTSTATUS
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_request_repository import TrainingRequestRepository
from dto.training_request_api_dto import (
    ApproveTrainingRequestDTO,
    CreatePersonalizedTrainingRequestDTO,
    CreatePlannedTrainingRequestDTO,
    RejectTrainingRequestDTO,
)
from errors.training_request_errors import (
    ActiveParticipationConflict,
    RelatedEntityNotFound,
    TrainingRequestConflict,
    TrainingRequestNotFound,
)
from models import Base
from models.access_level import AccessLevel
from models.domaine import Domaine
from models.employee import Employee
from models.participation import Participation
from models.role import Role
from models.training import Training
from models.training_request import TrainingRequest
from services.training_request_service import TrainingRequestService
from services.training_request_workflow_service import TrainingRequestWorkflowService


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
    current_session.add_all(
        [
            AccessLevel(id_access_level=1, label="Employee", level=1),
            Role(id_role=1, denomination_role="Employee", id_access_level=1),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
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
                first_name="Grace",
                last_name="Hopper",
                hash_password="hash",
                mail="grace@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Training(
                id_training=1,
                title="REST API",
                id_domaine=1,
                start_=date(2026, 1, 1),
                end_=date(2026, 1, 2),
                is_deleted=False,
            ),
            Training(
                id_training=2,
                title="Deleted training",
                id_domaine=1,
                is_deleted=True,
            ),
        ]
    )
    current_session.commit()
    yield current_session
    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def request_service(session):
    return TrainingRequestService(
        TrainingRequestRepository(session),
        EmployeeRepository(session),
        TrainingRepository(session),
    )


def workflow_service(session, participation_repository=None):
    return TrainingRequestWorkflowService(
        TrainingRequestRepository(session),
        EmployeeRepository(session),
        TrainingRepository(session),
        participation_repository or ParticipationRepository(session),
    )


def add_request(session, *, request_id, training_id=None, status="PENDING", deleted=False):
    request = TrainingRequest(
        id_training_request=request_id,
        id_employee=1,
        id_training=training_id,
        request_desc=None if training_id else "Kubernetes",
        status=status,
        reason=None,
        requested_at=date.today(),
        id_validator=None,
        is_deleted=deleted,
    )
    session.add(request)
    session.commit()
    return request


def test_create_planned_forces_server_values(session):
    result = request_service(session).create_planned(
        CreatePlannedTrainingRequestDTO(id_employee=1, id_training=1)
    )

    assert result.status == TRAININGREQUESTSTATUS.PENDING.value
    assert result.id_training == 1
    assert result.request_desc is None
    assert result.reason is None
    assert result.id_validator is None


def test_create_personalized_preserves_description_and_forces_server_values(session):
    result = request_service(session).create_personalized(
        CreatePersonalizedTrainingRequestDTO(
            id_employee=1,
            request_desc="Formation Kubernetes",
        )
    )

    assert result.status == TRAININGREQUESTSTATUS.PENDING.value
    assert result.id_training is None
    assert result.request_desc == "Formation Kubernetes"
    assert result.reason is None
    assert result.id_validator is None


def test_create_personalized_rejects_blank_description():
    with pytest.raises(ValueError):
        CreatePersonalizedTrainingRequestDTO(id_employee=1, request_desc="  ")


def test_approve_planned_creates_registered_participation(session):
    add_request(session, request_id=1, training_id=1)

    result = workflow_service(session).approve(
        1,
        ApproveTrainingRequestDTO(id_validator=2),
    )
    session.commit()

    participation = session.get(Participation, (1, 1))
    assert result.status == TRAININGREQUESTSTATUS.VALIDATED.value
    assert result.id_validator == 2
    assert participation.status == PARTICIPATIONSTATUS.REGISTERED.value


def test_approve_personalized_requires_and_assigns_training(session):
    add_request(session, request_id=1)

    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(id_validator=2),
        )
    session.rollback()

    result = workflow_service(session).approve(
        1,
        ApproveTrainingRequestDTO(id_validator=2, id_training=1),
    )
    assert result.id_training == 1


def test_approve_planned_rejects_training_override(session):
    add_request(session, request_id=1, training_id=1)

    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(id_validator=2, id_training=1),
        )


def test_reject_records_reason_and_creates_no_participation(session):
    add_request(session, request_id=1, training_id=1)

    result = workflow_service(session).reject(
        1,
        RejectTrainingRequestDTO(id_validator=2, reason="Not relevant"),
    )
    session.commit()

    assert result.status == TRAININGREQUESTSTATUS.REFUSED.value
    assert result.reason == "Not relevant"
    assert session.query(Participation).count() == 0


def test_approve_rejects_missing_or_deleted_related_entities(session):
    add_request(session, request_id=1, training_id=2)
    with pytest.raises(RelatedEntityNotFound):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(id_validator=2))
    session.rollback()

    add_request(session, request_id=2, training_id=1)
    session.get(Employee, 2).is_deleted = True
    session.commit()
    with pytest.raises(RelatedEntityNotFound):
        workflow_service(session).approve(2, ApproveTrainingRequestDTO(id_validator=2))


def test_processed_deleted_and_duplicate_requests_are_rejected(session):
    add_request(session, request_id=1, training_id=1, status="VALIDATED")
    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(id_validator=2))

    add_request(session, request_id=2, training_id=1)
    session.add(Participation(
        id_employee=1,
        id_training=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        is_deleted=True,
    ))
    session.commit()
    with pytest.raises(ActiveParticipationConflict):
        workflow_service(session).approve(2, ApproveTrainingRequestDTO(id_validator=2))


def test_active_duplicate_participation_keeps_request_unchanged(session):
    add_request(session, request_id=1, training_id=1)
    existing = Participation(
        id_employee=1,
        id_training=1,
        status=PARTICIPATIONSTATUS.IN_PROGRESS.value,
        is_deleted=False,
    )
    session.add(existing)
    session.commit()

    with pytest.raises(ActiveParticipationConflict):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(id_validator=2),
        )

    session.rollback()
    request = session.get(TrainingRequest, 1)
    participation = session.get(Participation, (1, 1))
    assert request.status == TRAININGREQUESTSTATUS.PENDING.value
    assert request.id_validator is None
    assert session.query(Participation).count() == 1
    assert participation.status == PARTICIPATIONSTATUS.IN_PROGRESS.value
    assert participation.is_deleted is False


def test_get_existing_finds_soft_deleted_participation(session):
    participation = Participation(
        id_employee=1,
        id_training=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        is_deleted=True,
    )
    session.add(participation)
    session.commit()

    repository = ParticipationRepository(session)

    assert repository.get_existing(1, 1) is participation
    assert repository.get_one((1, 1)) is participation


def test_approve_is_atomic_when_participation_creation_fails(session):
    add_request(session, request_id=1, training_id=1)

    class FailingParticipationRepository(ParticipationRepository):
        def add(self, entity):
            raise RuntimeError("participation insert failed")

    with pytest.raises(RuntimeError):
        workflow_service(
            session,
            FailingParticipationRepository(session),
        ).approve(1, ApproveTrainingRequestDTO(id_validator=2))

    session.rollback()
    session.expire_all()
    request = session.get(TrainingRequest, 1)
    assert request.status == TRAININGREQUESTSTATUS.PENDING.value
    assert request.id_validator is None
    assert session.get(Participation, (1, 1)) is None


def test_dto_rejects_non_positive_identifiers():
    with pytest.raises(ValueError):
        CreatePlannedTrainingRequestDTO(id_employee=0, id_training=1)
    with pytest.raises(ValueError):
        ApproveTrainingRequestDTO(id_validator=0)
