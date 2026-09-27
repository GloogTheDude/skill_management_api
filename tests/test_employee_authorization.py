from types import SimpleNamespace

import pytest

from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import TrainingRequestForbidden
from services.training_request_authorization import TrainingRequestAuthorization


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
    TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
        actor(1, 1), target(1)
    )
    TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
        actor(2, 2), target(1, 2)
    )
    TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
        actor(3, 3), target(99, 42)
    )


def test_employee_and_manager_out_of_scope_are_forbidden():
    with pytest.raises(TrainingRequestForbidden):
        TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
            actor(1, 1), target(2, 1)
        )
    with pytest.raises(TrainingRequestForbidden):
        TrainingRequestAuthorization.require_self_or_direct_manager_or_hr(
            actor(2, 2), target(4, 99)
        )


def test_available_training_scope_is_self_only():
    TrainingRequestAuthorization.require_self(actor(1, 1), 1)
    with pytest.raises(TrainingRequestForbidden):
        TrainingRequestAuthorization.require_self(actor(1, 1), 2)


@pytest.mark.parametrize("level", [1, 2])
def test_employee_crud_requires_hr(level):
    with pytest.raises(TrainingRequestForbidden):
        TrainingRequestAuthorization.require_hr(actor(1, level))
    TrainingRequestAuthorization.require_hr(actor(3, 3))
