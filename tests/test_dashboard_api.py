from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.constants import PermissionProfile, PARTICIPATIONSTATUS
from db.repositories.employee_repository import EmployeeRepository
from dto.auth_dto import AuthEmployeeDTO
from models import Base
from models.access_level import AccessLevel
from models.employee import Employee
from models.participation import Participation
from models.role import Role
from models.training import Training
from models.training_request import TrainingRequest
from services.dashboard_service import DashboardService


def actor(employee_id, profile):
    return AuthEmployeeDTO(
        id_employee=employee_id,
        first_name="Actor",
        last_name="Test",
        mail="actor@example.com",
        role_name=None,
        access_level_label=None,
        access_level=None,
        permission_profile=profile,
    )


def make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        AccessLevel(id_access_level=1, label="Employee", level=99, permission_profile="EMPLOYEE"),
        AccessLevel(id_access_level=2, label="Manager", level=1, permission_profile="MANAGER"),
        AccessLevel(id_access_level=3, label="HR", level=42, permission_profile="HR"),
        Role(id_role=1, denomination_role="Employee", id_access_level=1, is_deleted=False),
        Role(id_role=2, denomination_role="Manager", id_access_level=2, is_deleted=False),
        Role(id_role=3, denomination_role="HR", id_access_level=3, is_deleted=False),
        Employee(id_employee=1, first_name="Manager", id_role=2, is_deleted=False),
        Employee(id_employee=2, first_name="Direct", id_role=1, id_manager=1, is_deleted=False),
        Employee(id_employee=3, first_name="Other", id_role=1, is_deleted=False),
        Employee(id_employee=4, first_name="HR", id_role=3, is_deleted=False),
    ])
    session.commit()
    return engine, session


def test_dashboard_scopes_pending_and_active_items():
    engine, session = make_session()
    training = Training(
        id_training=1, title="Python", start_=date.today(), end_=date.today() + timedelta(days=1), is_deleted=False
    )
    session.add(training)
    session.add_all([
        TrainingRequest(id_training_request=1, id_employee=2, id_training=1, status="PENDING", requested_at=date.today(), is_deleted=False),
        TrainingRequest(id_training_request=2, id_employee=3, id_training=1, status="PENDING", requested_at=date.today(), is_deleted=False),
        Participation(id_employee=2, id_training=1, status=PARTICIPATIONSTATUS.REGISTERED.value, is_deleted=False),
    ])
    session.commit()

    manager = DashboardService(session).get_dashboard(actor(1, PermissionProfile.MANAGER))
    assert manager.pending_training_requests == 1
    assert manager.active_participations == 1
    assert manager.active_employees == 2

    hr = DashboardService(session).get_dashboard(actor(4, PermissionProfile.HR))
    assert hr.pending_training_requests == 2
    assert hr.active_participations == 1
    assert hr.active_employees == 4

    employee = DashboardService(session).get_dashboard(actor(2, PermissionProfile.EMPLOYEE))
    assert employee.pending_training_requests == 1
    assert employee.active_participations == 1
    assert employee.acquired_skills == 0
    assert employee.evaluated_skills == 0

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_dashboard_ignores_deleted_requests_and_participations():
    engine, session = make_session()
    session.add_all([
        TrainingRequest(id_training_request=1, id_employee=2, status="PENDING", requested_at=date.today(), is_deleted=True),
        Participation(id_employee=2, id_training=99, status=PARTICIPATIONSTATUS.REGISTERED.value, is_deleted=True),
    ])
    session.commit()

    dashboard = DashboardService(session).get_dashboard(actor(2, PermissionProfile.EMPLOYEE))
    assert dashboard.pending_training_requests == 0
    assert dashboard.active_participations == 0

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
