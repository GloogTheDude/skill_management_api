import asyncio
import inspect

import pytest
from fastapi import HTTPException

from controlers.auth_controller import require_hr_employee
from dto.auth_dto import AuthEmployeeDTO


def employee(level: int) -> AuthEmployeeDTO:
    return AuthEmployeeDTO(
        id_employee=level,
        first_name="Test",
        last_name="User",
        mail="test@example.com",
        role_name=None,
        access_level_label=None,
        access_level=level,
    )


@pytest.mark.parametrize("level", [1, 2])
def test_reference_mutation_dependency_rejects_non_hr(level):
    with pytest.raises(HTTPException) as error:
        asyncio.run(require_hr_employee(employee(level)))
    assert error.value.status_code == 403


def test_reference_mutation_dependency_accepts_only_hr():
    assert asyncio.run(require_hr_employee(employee(3))).access_level == 3


def test_reference_controllers_expose_auth_dependencies():
    controller_modules = (
        "controlers.domaine_controler",
        "controlers.skill_controler",
        "controlers.training_controller",
        "controlers.training_source_controler",
        "controlers.certification_controler",
        "controlers.diploma_controler",
        "controlers.role_controller",
        "controlers.access_level_controller",
    )
    for module_name in controller_modules:
        module = __import__(module_name, fromlist=["router"])
        for route in module.router.routes:
            dependencies = inspect.signature(route.endpoint).parameters.values()
            dependency_names = {
                getattr(parameter.default.dependency, "__name__", "")
                for parameter in dependencies
                if hasattr(parameter.default, "dependency")
            }
            assert "get_current_employee" in dependency_names or "require_hr_employee" in dependency_names
