import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.repositories.access_level_repository import AccessLevelRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.role_repository import RoleRepository
from errors.administrative_security_errors import LastHrAdministratorError
from models import AccessLevel, Base, Employee, Role
from services.access_level_service import AccessLevelService
from services.employee_service import EmployeeService
from services.role_service import RoleService
from dto.access_level_dto import UpdateAccessLevelDTO
from dto.role_dto import UpdateRoleDTO
from core.constants import PermissionProfile


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            AccessLevel(id_access_level=1, label="Employee", level=99, permission_profile="EMPLOYEE"),
            AccessLevel(id_access_level=2, label="HR", level=1, permission_profile="HR"),
            AccessLevel(id_access_level=3, label="HR second", level=42, permission_profile="HR"),
        ])
        session.add_all([
            Role(id_role=1, denomination_role="Developer", id_access_level=1),
            Role(id_role=2, denomination_role="HR", id_access_level=2),
            Role(id_role=3, denomination_role="HR second", id_access_level=3),
        ])
        session.flush()
        session.add_all([
            Employee(first_name="Alice", id_role=2),
            Employee(first_name="Bob", id_role=3),
        ])
        session.commit()
        yield session


def test_access_level_rank_does_not_change_permission_profile(session):
    access_level = session.get(AccessLevel, 1)
    assert access_level.level == 99
    assert access_level.permission_profile == PermissionProfile.EMPLOYEE.value


def test_last_hr_access_level_cannot_be_demoted(session):
    session.query(Employee).filter(Employee.id_employee == 2).update({Employee.id_role: 1})
    session.flush()
    service = AccessLevelService(AccessLevelRepository(session))
    with pytest.raises(LastHrAdministratorError):
        service.update(2, UpdateAccessLevelDTO(permission_profile=PermissionProfile.EMPLOYEE))


def test_one_of_two_hr_access_levels_can_be_demoted(session):
    service = AccessLevelService(AccessLevelRepository(session))
    result = service.update(2, UpdateAccessLevelDTO(permission_profile=PermissionProfile.EMPLOYEE))
    assert result.permission_profile == PermissionProfile.EMPLOYEE


def test_last_hr_role_and_employee_cannot_be_removed(session):
    session.query(Employee).filter(Employee.id_employee == 2).update({Employee.id_role: 1})
    session.flush()
    role_service = RoleService(RoleRepository(session))
    with pytest.raises(LastHrAdministratorError):
        role_service.update(2, UpdateRoleDTO(id_access_level=1))

    employee_service = EmployeeService(EmployeeRepository(session), RoleRepository(session))
    session.query(Employee).filter(Employee.id_employee == 2).update({Employee.id_role: 1})
    session.flush()
    with pytest.raises(LastHrAdministratorError):
        employee_service.delete(1)
