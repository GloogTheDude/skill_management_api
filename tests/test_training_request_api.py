from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from core.constants import PARTICIPATIONSTATUS, TRAININGREQUESTSTATUS
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_request_repository import TrainingRequestRepository
from dto.auth_dto import AuthEmployeeDTO
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
from errors.authorization_errors import AuthorizationForbidden
from models import Base
from models.access_level import AccessLevel
from models.domaine import Domaine
from models.employee import Employee
from models.participation import Participation
from models.role import Role
from models.training import Training
from models.training_request import TrainingRequest
from models.training_source import TrainingSource
from services.training_request_service import TrainingRequestService
from services.training_request_workflow_service import TrainingRequestWorkflowService
from services.training_request_queue_service import TrainingRequestQueueService
from controllers.auth_controller import get_current_employee
from controllers.training_request_controller import router as training_request_router
from main import app


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
            AccessLevel(id_access_level=2, label="Manager", level=2),
            AccessLevel(id_access_level=3, label="HR", level=3),
            Role(id_role=1, denomination_role="Employee", id_access_level=1),
            Role(id_role=2, denomination_role="Manager", id_access_level=2),
            Role(id_role=3, denomination_role="HR", id_access_level=3),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
            TrainingSource(id_source=1, name_source="Tech Provider", is_deleted=False),
            Employee(
                id_employee=1,
                first_name="Ada",
                last_name="Lovelace",
                hash_password="hash",
                mail="ada@example.com",
                id_role=1,
                id_manager=None,
                is_deleted=False,
            ),
            Employee(
                id_employee=2,
                first_name="Grace",
                last_name="Hopper",
                hash_password="hash",
                mail="grace@example.com",
                id_role=2,
                is_deleted=False,
            ),
            Employee(
                id_employee=3,
                first_name="Henri",
                last_name="Roe",
                hash_password="hash",
                mail="henri@example.com",
                id_role=3,
                is_deleted=False,
            ),
            Training(
                id_training=1,
                title="REST API",
                id_domaine=1,
                id_source=1,
                location="Sart Tilman — Bâtiment B37",
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
    current_session.get(Employee, 1).id_manager = 2
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


def actor(id_employee: int, access_level: int) -> AuthEmployeeDTO:
    return AuthEmployeeDTO(
        id_employee=id_employee,
        first_name="Actor",
        last_name="Test",
        mail="actor@example.com",
        role_name=None,
        access_level_label=None,
        access_level=access_level,
    )


def queue_service(session):
    return TrainingRequestQueueService(TrainingRequestRepository(session))


def add_queue_request(session, *, employee_id, training_id=None, status="PENDING", deleted=False):
    request = TrainingRequest(
        id_employee=employee_id,
        id_training=training_id,
        request_desc="custom request" if training_id is None else None,
        status=status,
        requested_at=date.today(),
        is_deleted=deleted,
    )
    session.add(request)
    session.flush()
    return request


def test_manager_queue_returns_direct_reports_and_both_request_types(session):
    planned = add_queue_request(session, employee_id=1, training_id=1)
    personalized = add_queue_request(session, employee_id=1)
    add_queue_request(session, employee_id=1, training_id=1, status="VALIDATED")
    add_queue_request(session, employee_id=2, training_id=1)
    session.commit()

    result = queue_service(session).get_for_manager(actor(2, 2))

    assert {item.id_training_request for item in result} == {
        planned.id_training_request,
        personalized.id_training_request,
    }
    planned_result = next(item for item in result if item.id_training_request == planned.id_training_request)
    personalized_result = next(item for item in result if item.id_training_request == personalized.id_training_request)
    assert planned_result.training_title == "REST API"
    assert planned_result.domaine_name == "Backend"
    assert planned_result.source_name == "Tech Provider"
    assert planned_result.location == "Sart Tilman — Bâtiment B37"
    assert planned_result.start_ == date(2026, 1, 1)
    assert planned_result.end_ == date(2026, 1, 2)
    assert planned_result.duration_hours is None
    assert planned_result.cost_hour is None
    assert planned_result.first_name_employee == "Ada"
    assert personalized_result.id_training is None
    assert personalized_result.training_title is None
    assert personalized_result.request_desc == "custom request"
    assert personalized_result.source_name is None
    assert personalized_result.location is None
    assert personalized_result.start_ is None
    assert personalized_result.end_ is None
    assert personalized_result.duration_hours is None
    assert personalized_result.cost_hour is None


def test_manager_queue_requires_manager_and_direct_scope(session):
    add_queue_request(session, employee_id=1, training_id=1)
    session.commit()

    with pytest.raises(AuthorizationForbidden):
        queue_service(session).get_for_manager(actor(1, 1))
    with pytest.raises(AuthorizationForbidden):
        queue_service(session).get_for_manager(actor(3, 3))


def test_hr_queue_returns_all_pending_and_requires_hr(session):
    first = add_queue_request(session, employee_id=1, training_id=1)
    second = add_queue_request(session, employee_id=2, training_id=1)
    add_queue_request(session, employee_id=1, training_id=1, status="REFUSED")
    deleted = add_queue_request(session, employee_id=1, training_id=1, deleted=True)
    session.commit()

    result = queue_service(session).get_for_hr(actor(3, 3))

    assert {item.id_training_request for item in result} == {
        first.id_training_request,
        second.id_training_request,
    }
    first_result = next(item for item in result if item.id_training_request == first.id_training_request)
    assert first_result.training_title == "REST API"
    assert first_result.domaine_name == "Backend"
    assert first_result.source_name == "Tech Provider"
    assert first_result.location == "Sart Tilman — Bâtiment B37"
    assert first_result.start_ == date(2026, 1, 1)
    assert first_result.end_ == date(2026, 1, 2)
    assert first_result.duration_hours is None
    assert first_result.cost_hour is None
    with pytest.raises(AuthorizationForbidden):
        queue_service(session).get_for_hr(actor(2, 2))
    with pytest.raises(AuthorizationForbidden):
        queue_service(session).get_for_hr(actor(1, 1))
    assert deleted.id_training_request not in {item.id_training_request for item in result}


def test_pending_queue_uses_one_sql_query(session):
    for _ in range(4):
        add_queue_request(session, employee_id=1, training_id=1)
    session.commit()
    statements = []

    def count_statement(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(session.bind, "before_cursor_execute", count_statement)
    try:
        result = queue_service(session).get_for_manager(actor(2, 2))
    finally:
        event.remove(session.bind, "before_cursor_execute", count_statement)

    assert len(result) == 4
    assert len(statements) == 1


def test_history_queue_is_scoped_and_contains_only_terminal_requests(session):
    validated = add_queue_request(session, employee_id=1, training_id=1, status="VALIDATED")
    refused = add_queue_request(session, employee_id=1, training_id=1, status="REFUSED")
    pending = add_queue_request(session, employee_id=1, training_id=1, status="PENDING")
    outside = add_queue_request(session, employee_id=2, training_id=1, status="VALIDATED")
    session.commit()

    result = queue_service(session).get_history_for_manager(actor(2, 2))
    assert {item.id_training_request for item in result} == {validated.id_training_request, refused.id_training_request}
    assert pending.id_training_request not in {item.id_training_request for item in result}
    assert outside.id_training_request not in {item.id_training_request for item in result}


def test_hr_history_queue_is_global(session):
    validated = add_queue_request(session, employee_id=1, training_id=1, status="VALIDATED")
    refused = add_queue_request(session, employee_id=2, training_id=1, status="REFUSED")
    session.commit()

    result = queue_service(session).get_history_for_hr(actor(3, 3))
    assert {item.id_training_request for item in result} == {validated.id_training_request, refused.id_training_request}


def test_mine_returns_all_request_statuses_and_personalized_requests(session):
    own_pending = add_queue_request(session, employee_id=1, training_id=1)
    own_personalized = add_queue_request(session, employee_id=1)
    own_personalized.status = "REFUSED"
    own_personalized.reason = "Not currently needed"
    own_deleted = add_queue_request(session, employee_id=1, training_id=1, deleted=True)
    other = add_queue_request(session, employee_id=2, training_id=1)
    session.commit()

    result = request_service(session).get_mine(actor(1, 1))

    assert {item.id_training_request for item in result} == {
        own_pending.id_training_request,
        own_personalized.id_training_request,
        own_deleted.id_training_request,
    }
    assert other.id_training_request not in {item.id_training_request for item in result}
    personalized = next(
        item for item in result if item.id_training_request == own_personalized.id_training_request
    )
    assert personalized.status == "REFUSED"
    assert personalized.reason == "Not currently needed"
    assert personalized.id_training is None
    assert personalized.training_title is None


def test_mine_uses_one_sql_query_for_multiple_requests(session):
    for _ in range(4):
        add_queue_request(session, employee_id=1, training_id=1)
    session.commit()
    statements = []

    def count_statement(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(session.bind, "before_cursor_execute", count_statement)
    try:
        result = request_service(session).get_mine(actor(1, 1))
    finally:
        event.remove(session.bind, "before_cursor_execute", count_statement)

    assert len(result) == 4
    assert len(statements) == 1


def add_request(
    session,
    *,
    request_id,
    training_id=None,
    status="PENDING",
    deleted=False,
    employee_id=1,
):
    request = TrainingRequest(
        id_training_request=request_id,
        id_employee=employee_id,
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
        1,
        CreatePlannedTrainingRequestDTO(id_training=1),
    )

    assert result.status == TRAININGREQUESTSTATUS.PENDING.value
    assert result.id_training == 1
    assert result.request_desc is None
    assert result.reason is None
    assert result.id_validator is None


def test_create_personalized_preserves_description_and_forces_server_values(session):
    result = request_service(session).create_personalized(
        1,
        CreatePersonalizedTrainingRequestDTO(
            request_desc="Formation Kubernetes",
        )
    )

    assert result.status == TRAININGREQUESTSTATUS.PENDING.value
    assert result.id_employee == 1
    assert result.id_training is None
    assert result.request_desc == "Formation Kubernetes"
    assert result.reason is None
    assert result.id_validator is None


def test_create_personalized_rejects_blank_description():
    with pytest.raises(ValueError):
        CreatePersonalizedTrainingRequestDTO(request_desc="  ")


def test_approve_planned_creates_registered_participation(session):
    add_request(session, request_id=1, training_id=1)

    result = workflow_service(session).approve(
        1,
        ApproveTrainingRequestDTO(),
        actor(2, 2),
    )
    session.commit()

    participation = session.get(Participation, (1, 1))
    assert result.status == TRAININGREQUESTSTATUS.VALIDATED.value
    assert result.id_validator == 2
    assert participation.status == PARTICIPATIONSTATUS.REGISTERED.value


def test_approve_personalized_requires_and_assigns_training(session):
    add_request(session, request_id=1)
    training = session.get(Training, 1)
    training.start_ = date.today() + timedelta(days=1)
    training.end_ = date.today() + timedelta(days=2)
    session.flush()

    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(),
            actor(2, 2),
        )
    session.rollback()
    training = session.get(Training, 1)
    training.start_ = date.today() + timedelta(days=1)
    training.end_ = date.today() + timedelta(days=2)
    session.flush()

    result = workflow_service(session).approve(
        1,
        ApproveTrainingRequestDTO(id_training=1),
        actor(2, 2),
    )
    assert result.id_training == 1


def test_approve_personalized_rejects_training_unavailable_for_employee(session):
    add_request(session, request_id=1)
    session.add(TrainingRequest(
        id_training_request=2,
        id_employee=1,
        id_training=1,
        status=TRAININGREQUESTSTATUS.PENDING.value,
        requested_at=date.today(),
        is_deleted=False,
    ))
    session.commit()

    with pytest.raises(TrainingRequestConflict, match="not available"):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(id_training=1),
            actor(2, 2),
        )


def test_approve_planned_rejects_training_override(session):
    add_request(session, request_id=1, training_id=1)

    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(
            1,
            ApproveTrainingRequestDTO(id_training=1),
            actor(2, 2),
        )


def test_reject_records_reason_and_creates_no_participation(session):
    add_request(session, request_id=1, training_id=1)

    result = workflow_service(session).reject(
        1,
        RejectTrainingRequestDTO(reason="Not relevant"),
        actor(2, 2),
    )
    session.commit()

    assert result.status == TRAININGREQUESTSTATUS.REFUSED.value
    assert result.reason == "Not relevant"
    assert session.query(Participation).count() == 0


def test_employee_cannot_approve_or_reject(session):
    add_request(session, request_id=1, training_id=1)
    with pytest.raises(AuthorizationForbidden):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(), actor(1, 1))

    session.rollback()
    add_request(session, request_id=2, training_id=1)
    with pytest.raises(AuthorizationForbidden):
        workflow_service(session).reject(
            2,
            RejectTrainingRequestDTO(reason="Not relevant"),
            actor(1, 1),
        )


def test_manager_cannot_process_request_outside_direct_reports(session):
    add_request(session, request_id=1, training_id=1, employee_id=2)

    with pytest.raises(AuthorizationForbidden):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(), actor(2, 2))

    session.rollback()
    add_request(session, request_id=2, training_id=1, employee_id=2)
    with pytest.raises(AuthorizationForbidden):
        workflow_service(session).reject(
            2,
            RejectTrainingRequestDTO(reason="Not relevant"),
            actor(2, 2),
        )


def test_hr_can_approve_request_outside_manager_scope(session):
    add_request(session, request_id=1, training_id=1, employee_id=2)

    result = workflow_service(session).approve(1, ApproveTrainingRequestDTO(), actor(3, 3))

    assert result.status == TRAININGREQUESTSTATUS.VALIDATED.value
    assert result.id_validator == 3


def test_hr_can_reject_request_outside_manager_scope(session):
    add_request(session, request_id=1, training_id=1, employee_id=2)

    result = workflow_service(session).reject(
        1,
        RejectTrainingRequestDTO(reason="Not relevant"),
        actor(3, 3),
    )

    assert result.status == TRAININGREQUESTSTATUS.REFUSED.value
    assert result.id_validator == 3


def test_approve_rejects_missing_or_deleted_related_entities(session):
    add_request(session, request_id=1, training_id=2)
    with pytest.raises(RelatedEntityNotFound):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(), actor(2, 2))
    session.rollback()

    add_request(session, request_id=2, training_id=1)
    session.get(Employee, 1).is_deleted = True
    session.commit()
    with pytest.raises(RelatedEntityNotFound):
        workflow_service(session).approve(2, ApproveTrainingRequestDTO(), actor(3, 3))


def test_processed_deleted_and_duplicate_requests_are_rejected(session):
    add_request(session, request_id=1, training_id=1, status="VALIDATED")
    with pytest.raises(TrainingRequestConflict):
        workflow_service(session).approve(1, ApproveTrainingRequestDTO(), actor(2, 2))

    add_request(session, request_id=2, training_id=1)
    session.add(Participation(
        id_employee=1,
        id_training=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        is_deleted=True,
    ))
    session.commit()
    with pytest.raises(ActiveParticipationConflict):
        workflow_service(session).approve(2, ApproveTrainingRequestDTO(), actor(2, 2))


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
            ApproveTrainingRequestDTO(),
            actor(2, 2),
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
        ).approve(1, ApproveTrainingRequestDTO(), actor(2, 2))

    session.rollback()
    session.expire_all()
    request = session.get(TrainingRequest, 1)
    assert request.status == TRAININGREQUESTSTATUS.PENDING.value
    assert request.id_validator is None
    assert session.get(Participation, (1, 1)) is None


def test_dto_rejects_non_positive_identifiers():
    with pytest.raises(ValueError):
        CreatePlannedTrainingRequestDTO(id_training=0)
    with pytest.raises(ValueError):
        ApproveTrainingRequestDTO(id_training=0)


def test_self_service_creation_contract_uses_session_identity():
    schema = app.openapi()
    planned = schema["paths"]["/training-requests/planned"]["post"]
    personalized = schema["paths"]["/training-requests/personalized"]["post"]

    planned_properties = planned["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    personalized_properties = personalized["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schemas = schema["components"]["schemas"]

    assert "id_employee" not in schemas[planned_properties.rsplit("/", 1)[-1]]["properties"]
    assert "id_employee" not in schemas[personalized_properties.rsplit("/", 1)[-1]]["properties"]
    assert "id_training" in schemas[planned_properties.rsplit("/", 1)[-1]]["properties"]
    assert "request_desc" in schemas[personalized_properties.rsplit("/", 1)[-1]]["properties"]

    for path in ("/training-requests/planned", "/training-requests/personalized"):
        route = next(
            route
            for route in training_request_router.routes
            if route.path == path
        )
        assert any(dependency.call is get_current_employee for dependency in route.dependant.dependencies)
