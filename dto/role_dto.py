from pydantic import BaseModel, Field

from models.role import Role


class ResponseRoleDTO(BaseModel):
    id_role: int
    denomination_role: str | None

    id_access_level: int
    access_level_label: str
    access_level: int

    @classmethod
    def from_entity(
        cls,
        role: Role,
    ):
        return cls(
            id_role=role.id_role,
            denomination_role=role.denomination_role,
            id_access_level=role.id_access_level,
            access_level_label=role.access_level.label,
            access_level=role.access_level.level,
        )


class CreateRoleDTO(BaseModel):
    denomination_role: str | None = Field(
        default=None,
        max_length=50,
    )
    id_access_level: int = Field(
        default=1,
        gt=0,
    )


class UpdateRoleDTO(BaseModel):
    denomination_role: str | None = Field(
        default=None,
        max_length=50,
    )
    id_access_level: int | None = Field(
        default=None,
        gt=0,
    )