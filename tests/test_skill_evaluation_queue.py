from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.constants import PermissionProfile, PARTICIPATIONSTATUS
from db.repositories.skill_validation_repository import SkillValidationRepository
from dto.skill_validation_dto import CreateSkillValidationDTO
from models import Base, AccessLevel, Domaine, Employee, Participation, Role, Skill, Training, TrainingSkill, ValidationType
from services.skill_validation_service import SkillValidationService


def make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        AccessLevel(id_access_level=1, label="Employee", level=99, permission_profile=PermissionProfile.EMPLOYEE.value),
        AccessLevel(id_access_level=2, label="Manager", level=1, permission_profile=PermissionProfile.MANAGER.value),
        Role(id_role=1, denomination_role="Employee", id_access_level=1),
        Role(id_role=2, denomination_role="Manager", id_access_level=2),
        Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
        Employee(id_employee=1, first_name="Manager", id_role=2, is_deleted=False),
        Employee(id_employee=2, first_name="Direct", id_role=1, id_manager=1, is_deleted=False),
        Employee(id_employee=3, first_name="Other", id_role=1, is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
        Skill(id_skill=2, name_skill="SQL", id_domaine=1, is_deleted=False),
        Training(id_training=1, title="Python course", id_domaine=1, is_deleted=False),
        TrainingSkill(id_training=1, id_skill=1, granted_level=4, is_deleted=False),
        Participation(id_employee=2, id_training=1, status=PARTICIPATIONSTATUS.COMPLETED.value, is_deleted=False),
        ValidationType(id_validation=1, source="internal", denomination_validation="Review", is_deleted=False),
    ])
    session.commit()
    return engine, session


def test_pending_queue_is_batch_scoped_and_current_validation_removes_item():
    engine, session = make_session()
    service = SkillValidationService(SkillValidationRepository(session))

    pending = service.get_pending_evaluations(1, PermissionProfile.MANAGER)
    assert [(item.id_employee, item.id_skill, item.acquired_level) for item in pending] == [(2, 1, 4)]

    service.create(CreateSkillValidationDTO(id_employee=2, id_skill=1, id_validation=1, level_skill=3), 1)
    assert service.get_pending_evaluations(1, PermissionProfile.MANAGER) == []
    assert service.get_pending_evaluations(1, PermissionProfile.EMPLOYEE) == []

    session.close()
    engine.dispose()


def test_history_queue_contains_current_validation_and_excludes_other_scope():
    engine, session = make_session()
    service = SkillValidationService(SkillValidationRepository(session))
    service.create(CreateSkillValidationDTO(id_employee=2, id_skill=1, id_validation=1, level_skill=3), 1)

    history = service.get_evaluation_history(1, PermissionProfile.MANAGER)
    assert len(history) == 1
    assert history[0].employee_first_name == "Direct"
    assert history[0].skill_name == "Python"

    session.close()
    engine.dispose()
