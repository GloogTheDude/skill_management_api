import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from dto.skill_link_replacement_dto import ReplaceSkillsDTO, ReplaceTrainingSkillsDTO
from models import Base
from models.certification import Certification
from models.certification_skill import CertificationSkill
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.domaine import Domaine
from models.training_source import TrainingSource
from models.skill import Skill
from models.training import Training
from models.training_skill import TrainingSkill
from services.skill_link_replacement_service import SkillLinkReplacementService
from services.training_support_service import TrainingSupportService
from services.training_service import TrainingService
from errors.training_errors import TrainingLifecycleConflict
from db.repositories.training_repository import TrainingRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_dto import CreateTrainingDTO, UpdateTrainingDTO
from models.training_request import TrainingRequest
from models.participation import Participation
from datetime import date
from decimal import Decimal


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
        TrainingSource(id_source=1, name_source="Internal", is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
        Skill(id_skill=2, name_skill="SQL", id_domaine=1, is_deleted=False),
        Skill(id_skill=3, name_skill="Rust", id_domaine=1, is_deleted=False),
        Skill(id_skill=4, name_skill="Go", id_domaine=1, is_deleted=False),
        Skill(id_skill=5, name_skill="Java", id_domaine=1, is_deleted=False),
        Training(id_training=1, title="T", id_domaine=1, id_diploma=1, is_deleted=False),
        Diploma(id_diploma=1, subject_diploma="D", id_domaine=1, is_deleted=False),
        Certification(id_certification=1, subject_certification="C", id_domaine=1, is_deleted=False),
    ])
    session.commit()
    yield session
    session.close()


@pytest.mark.parametrize(
    ("aggregate", "link", "aggregate_key", "level_key"),
    [
        (Training, TrainingSkill, "id_training", "granted_level"),
        (Diploma, DiplomaSkill, "id_diploma", "min_level"),
        (Certification, CertificationSkill, "id_certification", "granted_level"),
    ],
)
def test_replacement_reactivates_and_soft_deletes_consistently(
    session, aggregate, link, aggregate_key, level_key
):
    def get_link(skill_id):
        return session.query(link).filter(
            getattr(link, aggregate_key) == 1,
            link.id_skill == skill_id,
        ).one()

    service = SkillLinkReplacementService(session)
    service.replace(aggregate, 1, aggregate_key, link, "id_skill", level_key, [(1, 2), (2, 3)])
    original = get_link(2)
    service.replace(aggregate, 1, aggregate_key, link, "id_skill", level_key, [(2, 4), (3, 1)])
    assert get_link(1).is_deleted is True
    assert get_link(2) is original
    assert get_link(2).is_deleted is False
    assert get_link(2).__getattribute__(level_key) == 4
    assert get_link(3).is_deleted is False

    service.replace(aggregate, 1, aggregate_key, link, "id_skill", level_key, [(1, 5)])
    assert get_link(1).is_deleted is False


def test_empty_replacement_soft_deletes_all_active_links(session):
    service = SkillLinkReplacementService(session)
    service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [(1, 2), (2, 3)])
    service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [])
    assert all(link.is_deleted for link in session.query(TrainingSkill).all())


def test_invalid_skill_is_rejected_before_existing_links_change(session):
    service = SkillLinkReplacementService(session)
    service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [(1, 2)])
    with pytest.raises(LookupError):
        service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [(2, 3), (99, 1)])
    link = session.query(TrainingSkill).one()
    assert link.id_skill == 1
    assert link.is_deleted is False


@pytest.mark.parametrize("model, identifier", [
    (Training, 99), (Diploma, 99), (Certification, 99),
])
def test_missing_aggregate_is_rejected(session, model, identifier):
    with pytest.raises(LookupError):
        SkillLinkReplacementService(session).replace(
            model, identifier,
            {Training: "id_training", Diploma: "id_diploma", Certification: "id_certification"}[model],
            {Training: TrainingSkill, Diploma: DiplomaSkill, Certification: CertificationSkill}[model],
            "id_skill", "granted_level", [(1, 1)],
        )


def test_training_level_is_required_and_positive():
    with pytest.raises(ValidationError):
        ReplaceTrainingSkillsDTO(skills=[{"id_skill": 1}])
    with pytest.raises(ValidationError):
        ReplaceTrainingSkillsDTO(skills=[{"id_skill": 1, "level": 0}])


def test_replacement_query_count_is_constant_for_one_or_many_skills(session):
    statements = []
    def count_selects(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)
    event.listen(session.bind, "before_cursor_execute", count_selects)
    service = SkillLinkReplacementService(session)
    service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [(1, 2)])
    one_count = len(statements)
    statements.clear()
    service.replace(Training, 1, "id_training", TrainingSkill, "id_skill", "granted_level", [(1, 2), (2, 3), (3, 4)])
    many_count = len(statements)
    event.remove(session.bind, "before_cursor_execute", count_selects)
    assert many_count == one_count


def test_training_without_target_cannot_remove_last_support(session):
    training = Training(id_training=2, title="Skills", id_domaine=1, is_deleted=False)
    session.add(training)
    session.flush()
    service = TrainingSupportService(session)
    service.replace_skills(2, [(1, 2)])

    with pytest.raises(ValueError):
        service.replace_skills(2, [])

    assert session.query(TrainingSkill).filter_by(id_training=2).one().is_deleted is False


def test_skill_only_training_cannot_remove_its_last_skill(session):
    session.add(Training(id_training=2, title="Skills", id_domaine=1, id_source=1, is_deleted=False))
    session.flush()
    service = TrainingSupportService(session)
    service.replace_skills(2, [(1, 2)])
    with pytest.raises(ValueError):
        service.replace_skills(2, [])
    assert session.query(TrainingSkill).filter_by(id_training=2).one().is_deleted is False


def test_support_mode_rejects_direct_skills_with_diploma_or_certification(session):
    with pytest.raises(ValueError):
        TrainingSupportService(session).replace_skills(1, [(1, 2)])


def test_used_training_cannot_change_structure_or_skills(session):
    session.add(Training(id_training=2, title="Used", id_domaine=1, id_source=1,
                         start_=date(2030, 1, 1), end_=date(2030, 1, 2),
                         is_deleted=False))
    session.flush()
    session.add(TrainingRequest(
        id_training_request=1,
        id_employee=999,
        id_training=2,
        status="PENDING",
        requested_at=date.today(),
        is_deleted=True,
    ))
    session.commit()
    service = TrainingService(
        TrainingRepository(session),
        DomaineRepository(session),
        TrainingSourceRepository(session),
    )

    service.update(2, UpdateTrainingDTO(title="Renamed", location="Room 1"))
    with pytest.raises(TrainingLifecycleConflict):
        service.update(2, UpdateTrainingDTO(start_=date(2031, 1, 1)))
    with pytest.raises(TrainingLifecycleConflict):
        TrainingSupportService(session).replace_skills(2, [(1, 3)])


def test_training_usage_is_detected_from_requests_or_participations(session):
    repository = TrainingRepository(session)
    session.add(Training(id_training=2, title="Tracked", id_domaine=1, id_source=1, is_deleted=False))
    session.flush()
    assert repository.is_used(2) is False
    session.add(TrainingRequest(id_training_request=2, id_employee=999, id_training=2,
                                status="PENDING", requested_at=date.today(), is_deleted=True))
    session.commit()
    assert repository.is_used(2) is True
    session.add(Participation(id_employee=999, id_training=1, status="COMPLETED", is_deleted=True))
    session.commit()
    assert repository.is_used(1) is True


def test_training_support_query_count_is_constant_for_one_or_five_skills(session):
    training = Training(id_training=3, title="Many skills", id_domaine=1, is_deleted=False)
    session.add(training)
    session.flush()
    statements = []

    def count_selects(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(session.bind, "before_cursor_execute", count_selects)
    service = TrainingSupportService(session)
    service.replace_skills(3, [(1, 1)])
    one_count = len(statements)
    statements.clear()
    service.replace_skills(3, [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)])
    five_count = len(statements)
    event.remove(session.bind, "before_cursor_execute", count_selects)
    assert five_count == one_count


def test_training_create_rolls_back_after_skill_sync_failure(session, monkeypatch):
    def fail_after_creation(*args, **kwargs):
        raise RuntimeError("skill synchronization failed")

    monkeypatch.setattr(TrainingSupportService, "replace_skills", fail_after_creation)
    service = TrainingService(
        TrainingRepository(session),
        DomaineRepository(session),
        TrainingSourceRepository(session),
    )

    with pytest.raises(RuntimeError):
        service.create(CreateTrainingDTO(
            title="Atomic",
            id_domaine=1,
            id_source=1,
            start_=date(2030, 1, 1),
            end_=date(2030, 1, 2),
            cost_hour=Decimal("1"),
            duration_hours=Decimal("1"),
            skills=[{"id_skill": 1, "level": 1}],
        ))
    session.rollback()
    assert session.query(Training).filter_by(title="Atomic").count() == 0
    assert session.query(TrainingSkill).filter_by(id_skill=1).count() == 0


@pytest.mark.parametrize("dto_type", [ReplaceSkillsDTO, ReplaceTrainingSkillsDTO])
def test_replacement_rejects_duplicate_skill_ids(dto_type):
    with pytest.raises(ValidationError):
        dto_type(skills=[{"id_skill": 1, "level": 2}, {"id_skill": 1, "level": 3}])
