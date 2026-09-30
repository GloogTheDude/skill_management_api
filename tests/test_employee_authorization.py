from types import SimpleNamespace

import pytest

from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from services.employee_authorization_service import EmployeeAuthorizationService
from core.constants import PermissionProfile


def actor(employee_id, level):
    return AuthEmployeeDTO(
        id_employee=employee_id,
        first_name="Actor",
        last_name="Test",
        mail="actor@example.com",
        role_name=None,
        access_level_label=None,
        access_level=level,
    )


def target(employee_id, manager_id=None):
    return SimpleNamespace(id_employee=employee_id, id_manager=manager_id)


def test_self_or_direct_manager_or_hr_scope():
    EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
        actor(1, 1), target(1)
    )
    EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
        actor(2, 2), target(1, 2)
    )
    EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
        actor(3, 3), target(99, 42)
    )


def test_employee_and_manager_out_of_scope_are_forbidden():
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
            actor(1, 1), target(2, 1)
        )
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
            actor(2, 2), target(4, 99)
        )


def test_manager_may_read_direct_report_acquisitions_but_not_other_employee():
    EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
        actor(2, 2), target(4, 2)
    )
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(
            actor(2, 2), target(5, 99)
        )


def test_acquisition_mutations_remain_hr_only():
    for level in (1, 2):
        with pytest.raises(AuthorizationForbidden):
            EmployeeAuthorizationService.require_hr(actor(1, level))
    EmployeeAuthorizationService.require_hr(actor(3, 3))


def test_available_training_scope_is_self_only():
    EmployeeAuthorizationService.require_self(actor(1, 1), 1)
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_self(actor(1, 1), 2)


@pytest.mark.parametrize("level", [1, 2])
def test_employee_crud_requires_hr(level):
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_hr(actor(1, level))
    EmployeeAuthorizationService.require_hr(actor(3, 3))


def test_rank_does_not_grant_manager_or_hr_permissions():
    executive = actor(1, 99)
    executive.permission_profile = PermissionProfile.EMPLOYEE

    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_manager_or_hr(executive)
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_hr(executive)


def test_arbitrary_rank_keeps_explicit_manager_and_hr_permissions():
    manager = actor(1, 47)
    manager.permission_profile = PermissionProfile.MANAGER
    hr = actor(2, 6)
    hr.permission_profile = PermissionProfile.HR

    EmployeeAuthorizationService.require_manager_or_hr(manager)
    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_hr(manager)
    EmployeeAuthorizationService.require_manager_or_hr(hr)
    EmployeeAuthorizationService.require_hr(hr)


def test_same_rank_different_profiles_have_different_permissions():
    employee = actor(1, 4)
    employee.permission_profile = PermissionProfile.EMPLOYEE
    manager = actor(2, 4)
    manager.permission_profile = PermissionProfile.MANAGER

    with pytest.raises(AuthorizationForbidden):
        EmployeeAuthorizationService.require_manager_or_hr(employee)
    EmployeeAuthorizationService.require_manager_or_hr(manager)
