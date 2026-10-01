import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.constants import PermissionProfile
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.role_repository import RoleRepository
from dto.employee_dto import UpdateEmployeeDTO
from models import AccessLevel, Base, Employee, Role
from services.employee_service import EmployeeService


@pytest.fixture
def hierarchy_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        AccessLevel(id_access_level=1, label="Employee", level=1, permission_profile=PermissionProfile.EMPLOYEE.value),
        AccessLevel(id_access_level=2, label="Manager", level=2, permission_profile=PermissionProfile.MANAGER.value),
        AccessLevel(id_access_level=3, label="HR", level=3, permission_profile=PermissionProfile.HR.value),
        Role(id_role=1, denomination_role="Employee", id_access_level=1),
        Role(id_role=2, denomination_role="Manager", id_access_level=2),
        Role(id_role=3, denomination_role="HR", id_access_level=3),
        Employee(id_employee=1, first_name="Alice", id_role=1, is_deleted=False),
        Employee(id_employee=2, first_name="Bob", id_role=1, is_deleted=False),
    ])
    session.commit()
    yield session
    session.close()
    engine.dispose()


def service(session):
    return EmployeeService(EmployeeRepository(session), RoleRepository(session))


def test_employee_profile_cannot_be_assigned_as_manager(hierarchy_session):
    with pytest.raises(ValueError, match="MANAGER|HR"):
        service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=1))


def test_self_management_is_rejected(hierarchy_session):
    with pytest.raises(ValueError, match="own manager"):
        service(hierarchy_session).update(1, UpdateEmployeeDTO(id_manager=1))


def test_archiving_manager_with_active_reports_is_rejected(hierarchy_session):
    manager = hierarchy_session.get(Employee, 1)
    manager.id_role = 2
    hierarchy_session.get(Employee, 2).id_manager = 1
    hierarchy_session.commit()

    with pytest.raises(ValueError, match="active direct reports"):
        service(hierarchy_session).delete(1)


def test_demoting_manager_with_active_reports_is_rejected(hierarchy_session):
    manager = hierarchy_session.get(Employee, 1)
    manager.id_role = 2
    hierarchy_session.get(Employee, 2).id_manager = 1
    hierarchy_session.commit()

    with pytest.raises(ValueError, match="direct reports"):
        service(hierarchy_session).update(1, UpdateEmployeeDTO(id_role=1))


def test_manager_and_hr_profiles_can_manage_and_null_is_allowed(hierarchy_session):
    hierarchy_session.get(Employee, 1).id_role = 2
    hierarchy_session.get(Employee, 2).id_role = 2
    hierarchy_session.flush()
    service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=1))
    service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=None))
    hierarchy_session.get(Employee, 1).id_role = 3
    hierarchy_session.flush()
    service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=1))


def test_missing_or_archived_manager_is_rejected(hierarchy_session):
    with pytest.raises(Exception):
        service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=999999))
    hierarchy_session.get(Employee, 1).is_deleted = True
    hierarchy_session.commit()
    with pytest.raises(Exception):
        service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=1))


def test_indirect_cycle_is_rejected(hierarchy_session):
    hierarchy_session.get(Employee, 1).id_role = 2
    hierarchy_session.get(Employee, 2).id_role = 2
    hierarchy_session.add(Employee(id_employee=3, first_name="Charlie", id_role=2, is_deleted=False))
    hierarchy_session.commit()
    service(hierarchy_session).update(2, UpdateEmployeeDTO(id_manager=1))
    service(hierarchy_session).update(3, UpdateEmployeeDTO(id_manager=2))
    with pytest.raises(ValueError, match="cycle"):
        service(hierarchy_session).update(1, UpdateEmployeeDTO(id_manager=3))
