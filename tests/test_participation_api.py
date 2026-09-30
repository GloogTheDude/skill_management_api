from datetime import date, timedelta
import asyncio
from io import BytesIO

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
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from errors.participation_errors import (
    ParticipationCannotCancel,
    ParticipationCannotStart,
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
from models.skill import Skill
from models.training_skill import TrainingSkill
from models.training_source import TrainingSource
from models.training_request import TrainingRequest
from models.validation_type import ValidationType
from models.skill_validation import SkillValidation
from services.participation_completion_service import ParticipationCompletionService
from services.participation_service import ParticipationService
from services.employee_skill_profile_service import EmployeeSkillProfileService
from services.document_storage import LocalDocumentStorage
from services.participation_document_service import ParticipationDocumentService
from services.training_request_workflow_service import TrainingRequestWorkflowService
from services.skill_validation_service import SkillValidationService
from db.repositories.training_request_repository import TrainingRequestRepository
from db.repositories.skill_validation_repository import SkillValidationRepository
from dto.training_request_api_dto import ApproveTrainingRequestDTO
from dto.skill_validation_dto import CreateSkillValidationDTO
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from starlette.datastructures import Headers
from starlette.datastructures import UploadFile


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
            Employee(
                id_employee=2,
                first_name="Grace",
                last_name="Hopper",
                hash_password="hash",
                mail="grace@example.com",
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
        EmployeeRepository(session),
    )


def document_actor(id_employee=1, access_level=3):
    return AuthEmployeeDTO(
        id_employee=id_employee,
        first_name="Actor",
        last_name="Test",
        mail="actor@example.com",
        role_name="HR",
        access_level_label="HR",
        access_level=access_level,
    )


def add_training_and_participation(
    session,
    *,
    training_id,
    employee_id=1,
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
        id_employee=employee_id,
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


def test_scoped_participations_include_training_details_and_nullable_fields(session):
    add_training_and_participation(session, training_id=1, end_=date.today())

    result = ParticipationService(ParticipationRepository(session)).get_all(1, 1)

    assert len(result) == 1
    assert result[0].employee_first_name == "Ada"
    assert result[0].training_title == "Training 1"
    assert result[0].domaine_name == "Backend"
    assert result[0].source_name == "Training provider"
    assert result[0].location is None
    assert result[0].start_ == date.today() - timedelta(days=10)
    assert result[0].end_ == date.today()
    assert result[0].duration_hours is None
    assert result[0].cost_hour is None


def test_manager_and_hr_receive_enriched_participations_without_scope_leak(session):
    session.get(Employee, 1).id_manager = 2
    session.commit()
    add_training_and_participation(session, training_id=1, employee_id=1, end_=date.today())
    add_training_and_participation(session, training_id=2, employee_id=2, end_=date.today())

    manager_result = ParticipationService(ParticipationRepository(session)).get_all(2, 2)
    assert {item.id_employee for item in manager_result} == {1, 2}
    assert all(item.training_title for item in manager_result)
    assert all(item.source_name == "Training provider" for item in manager_result)

    hr_result = ParticipationService(ParticipationRepository(session)).get_all(3, 3)
    assert {item.id_employee for item in hr_result} == {1, 2}
    assert all(item.training_title for item in hr_result)


@pytest.mark.parametrize(
    "status",
    [
        PARTICIPATIONSTATUS.COMPLETED.value,
        PARTICIPATIONSTATUS.FAILED.value,
        PARTICIPATIONSTATUS.ABSENT.value,
        PARTICIPATIONSTATUS.CANCELLED.value,
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


def test_start_moves_registered_to_in_progress(session):
    add_training_and_participation(
        session,
        training_id=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
    )

    started = completion_service(session).start(1, 1)

    assert started.status == PARTICIPATIONSTATUS.IN_PROGRESS.value


def test_hr_can_cancel_registered_participation_before_training_end(session):
    add_training_and_participation(
        session,
        training_id=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        end_=date.today() + timedelta(days=1),
    )

    cancelled = completion_service(session).cancel(1, 1)

    assert cancelled.status == PARTICIPATIONSTATUS.CANCELLED.value


@pytest.mark.parametrize("status", [
    PARTICIPATIONSTATUS.COMPLETED.value,
    PARTICIPATIONSTATUS.FAILED.value,
    PARTICIPATIONSTATUS.ABSENT.value,
    PARTICIPATIONSTATUS.CANCELLED.value,
])
def test_terminal_participation_cannot_be_cancelled(session, status):
    add_training_and_participation(session, training_id=1, status=status, end_=date.today())

    with pytest.raises(ParticipationCannotCancel):
        completion_service(session).cancel(1, 1)


def test_participation_cannot_be_cancelled_after_training_end(session):
    add_training_and_participation(
        session,
        training_id=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        end_=date.today(),
    )

    with pytest.raises(ParticipationCannotCancel):
        completion_service(session).cancel(1, 1)


@pytest.mark.parametrize(
    "status",
    [
        PARTICIPATIONSTATUS.IN_PROGRESS.value,
        PARTICIPATIONSTATUS.COMPLETED.value,
        PARTICIPATIONSTATUS.FAILED.value,
        PARTICIPATIONSTATUS.ABSENT.value,
        PARTICIPATIONSTATUS.CANCELLED.value,
    ],
)
def test_start_rejects_non_registered_status(session, status):
    add_training_and_participation(session, training_id=1, status=status)

    with pytest.raises(ParticipationCannotStart):
        completion_service(session).start(1, 1)


def test_full_cycle_completion_exposes_training_skill_in_profile(session):
    session.add(Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False))
    add_training_and_participation(
        session,
        training_id=1,
        status=PARTICIPATIONSTATUS.REGISTERED.value,
        end_=date.today(),
    )
    session.add(TrainingSkill(id_training=1, id_skill=1, granted_level=4, is_deleted=False))
    session.commit()

    completed = completion_service(session).close(1, 1, PARTICIPATIONSTATUS.COMPLETED.value)
    profile = EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    ).get_profile(1)

    assert completed.status == PARTICIPATIONSTATUS.COMPLETED.value
    python = next(skill for skill in profile if skill.skill_id == 1)


def test_training_request_to_evaluation_keeps_acquired_and_evaluated_separate(session):
    session.add_all([
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
        Training(
            id_training=1,
            title="Training 1",
            id_domaine=1,
            id_source=1,
            start_=date.today() - timedelta(days=10),
            end_=date.today(),
            is_deleted=False,
        ),
        TrainingSkill(id_training=1, id_skill=1, granted_level=3, is_deleted=False),
        TrainingRequest(
            id_training_request=1,
            id_employee=1,
            id_training=1,
            status="PENDING",
            requested_at=date.today(),
            is_deleted=False,
        ),
        ValidationType(
            id_validation=1,
            denomination_validation="Observation",
            is_deleted=False,
        ),
    ])
    session.commit()

    actor = document_actor(id_employee=2)
    workflow = TrainingRequestWorkflowService(
        TrainingRequestRepository(session),
        EmployeeRepository(session),
        TrainingRepository(session),
        ParticipationRepository(session),
    )
    workflow.approve(1, ApproveTrainingRequestDTO(), actor)
    completion_service(session).complete(1, 1)
    session.commit()

    profile = EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    ).get_profile(1)
    python = next(skill for skill in profile if skill.skill_id == 1)
    assert python.acquired_level == 3
    assert python.evaluated_level is None

    SkillValidationService(SkillValidationRepository(session)).create(
        CreateSkillValidationDTO(
            id_employee=1,
            id_skill=1,
            id_validation=1,
            level_skill=5,
        ),
        validator_id=2,
    )
    session.commit()
    profile = EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    ).get_profile(1)
    python = next(skill for skill in profile if skill.skill_id == 1)
    assert python.acquired_level == 3
    assert python.evaluated_level == 5


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


def test_complete_keeps_historical_participation_working_after_training_archive(session):
    add_training_and_participation(
        session,
        training_id=1,
        end_=date.today(),
        is_deleted=True,
    )

    completed = completion_service(session).complete(1, 1)
    assert completed.status == PARTICIPATIONSTATUS.COMPLETED.value


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


@pytest.mark.parametrize("result", [
    PARTICIPATIONSTATUS.FAILED.value,
    PARTICIPATIONSTATUS.ABSENT.value,
])
def test_failed_or_absent_training_creates_no_acquisition(session, result):
    add_training_and_participation(session, training_id=1, end_=date.today())
    session.add(Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False))
    session.add(TrainingSkill(id_training=1, id_skill=1, granted_level=4, is_deleted=False))
    session.commit()

    closed = completion_service(session).close(1, 1, result)
    session.commit()

    assert closed.status == result
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
        EmployeeRepository(session),
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
        training_id=6,
        employee_id=2,
        end_=date.today(),
    )
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

    assert len(result) == 4
    assert {
        (participation.id_employee, participation.id_training)
        for participation in result
    } == {(1, 1), (1, 2), (1, 4), (2, 6)}


def test_participation_document_upload_list_and_soft_delete(session, tmp_path):
    add_training_and_participation(session, training_id=1, end_=date.today())
    service = ParticipationDocumentService(session, LocalDocumentStorage(str(tmp_path)))
    upload = UploadFile(
        file=BytesIO(b"pdf-content"),
        filename="certificat.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    document = asyncio.run(service.upload(document_actor(), 1, 1, "CERTIFICATE", upload))
    assert document.original_filename == "certificat.pdf"
    assert document.mime_type == "application/pdf"
    assert document.size_bytes == len(b"pdf-content")
    assert not hasattr(document, "storage_key")
    assert (tmp_path / document.original_filename).exists() is False
    assert len(service.list(document_actor(), 1, 1)) == 1

    service.delete(document_actor(), document.id_participation_document)
    assert service.list(document_actor(), 1, 1) == []


def test_participation_document_scope_and_upload_policy(session, tmp_path):
    add_training_and_participation(session, training_id=1, employee_id=1, end_=date.today())
    add_training_and_participation(session, training_id=2, employee_id=2, end_=date.today())
    service = ParticipationDocumentService(session, LocalDocumentStorage(str(tmp_path)))
    upload = UploadFile(
        file=BytesIO(b"pdf-content"),
        filename="certificat.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    with pytest.raises(AuthorizationForbidden):
        service.list(document_actor(2, 1), 1, 1)
    with pytest.raises(ValueError):
        asyncio.run(service.upload(document_actor(), 1, 1, "CERTIFICATE", UploadFile(
            file=BytesIO(b"script"), filename="script.exe",
            headers=Headers({"content-type": "application/octet-stream"}),
        )))
