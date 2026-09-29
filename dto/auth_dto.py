from pydantic import BaseModel, Field, model_validator

from models.employee import Employee
from core.constants import PermissionProfile


class LoginDTO(BaseModel):
    mail: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthEmployeeDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    mail: str | None
    role_name: str | None
    access_level_label: str | None
    access_level: int | None
    permission_profile: PermissionProfile | None = None

    @model_validator(mode="after")
    def fill_legacy_permission_profile(self):
        if self.permission_profile is None:
            self.permission_profile = {
                1: PermissionProfile.EMPLOYEE,
                2: PermissionProfile.MANAGER,
                3: PermissionProfile.HR,
            }.get(self.access_level)
        return self

    @classmethod
    def from_entity(cls, employee: Employee) -> "AuthEmployeeDTO":
        role = employee.role
        access_level = role.access_level if role is not None else None
        return cls(
            id_employee=employee.id_employee,
            first_name=employee.first_name,
            last_name=employee.last_name,
            mail=employee.mail,
            role_name=role.denomination_role if role is not None else None,
            access_level_label=(
                access_level.label if access_level is not None else None
            ),
            access_level=access_level.level if access_level is not None else None,
            permission_profile=(
                PermissionProfile(access_level.permission_profile)
                if access_level is not None else None
            ),
        )
