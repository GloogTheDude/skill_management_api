from pydantic import BaseModel, Field

from models.access_level import AccessLevel
from core.constants import PermissionProfile


class ResponseAccessLevelDTO(BaseModel):
    id_access_level: int
    label: str
    level: int
    permission_profile: PermissionProfile

    @classmethod
    def from_entity(
        cls,
        access_level: AccessLevel,
    ):
        return cls(
            id_access_level=access_level.id_access_level,
            label=access_level.label,
            level=access_level.level,
            permission_profile=PermissionProfile(access_level.permission_profile),
        )


class CreateAccessLevelDTO(BaseModel):
    label: str = Field(
        min_length=1,
        max_length=50,
    )
    level: int
    permission_profile: PermissionProfile = PermissionProfile.EMPLOYEE


class UpdateAccessLevelDTO(BaseModel):
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    level: int | None = None
    permission_profile: PermissionProfile | None = None
