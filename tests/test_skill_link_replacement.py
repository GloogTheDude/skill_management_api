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
from models.skill import Skill
from models.training import Training
from models.training_skill import TrainingSkill
from services.skill_link_replacement_service import SkillLinkReplacementService


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
        Skill(id_skill=2, name_skill="SQL", id_domaine=1, is_deleted=False),
        Skill(id_skill=3, name_skill="Rust", id_domaine=1, is_deleted=False),
        Training(id_training=1, title="T", id_domaine=1, is_deleted=False),
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


@pytest.mark.parametrize("dto_type", [ReplaceSkillsDTO, ReplaceTrainingSkillsDTO])
def test_replacement_rejects_duplicate_skill_ids(dto_type):
    with pytest.raises(ValidationError):
        dto_type(skills=[{"id_skill": 1, "level": 2}, {"id_skill": 1, "level": 3}])
