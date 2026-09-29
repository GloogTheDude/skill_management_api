from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dto.skill_validation_dto import CreateSkillValidationDTO
from db.repositories.skill_validation_repository import SkillValidationRepository
from models import Base
from models.access_level import AccessLevel
from models.domaine import Domaine
from models.employee import Employee
from models.role import Role
from models.skill import Skill
from models.validation_type import ValidationType
from services.skill_validation_service import SkillValidationService


def test_new_validation_supersedes_previous_and_allows_level_decrease():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        AccessLevel(id_access_level=1, label="Employee", level=1),
        Role(id_role=1, denomination_role="Employee", id_access_level=1),
        Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
        Employee(id_employee=1, first_name="Daniel", id_role=1, is_deleted=False),
        Employee(id_employee=2, first_name="Alice", id_role=1, is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
        ValidationType(id_validation=1, source="manual", denomination_validation="Review", is_deleted=False),
    ])
    session.commit()
    service = SkillValidationService(SkillValidationRepository(session))

    first = service.create(CreateSkillValidationDTO(id_validation=1, id_employee=1, id_skill=1, level_skill=5), 2)
    second = service.create(CreateSkillValidationDTO(id_validation=1, id_employee=1, id_skill=1, level_skill=2), 2)
    history = service.get_history(1, 1)

    assert history[1].superseded_at is not None
    assert history[0].superseded_at is None
    assert history[0].level_skill == 2
    assert [item.id_skill_validation for item in history] == [second.id_skill_validation, first.id_skill_validation]
    assert all(item.validated_at is not None for item in history)
    session.close()
    engine.dispose()
