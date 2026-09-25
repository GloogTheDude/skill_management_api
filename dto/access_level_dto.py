from pydantic import BaseModel, Field

from models.access_level import AccessLevel


class ResponseAccessLevelDTO(BaseModel):
    id_access_level: int
    label: str
    level: int

    @classmethod
    def from_entity(
        cls,
        access_level: AccessLevel,
    ):
        return cls(
            id_access_level=access_level.id_access_level,
            label=access_level.label,
            level=access_level.level,
        )


class CreateAccessLevelDTO(BaseModel):
    label: str = Field(
        min_length=1,
        max_length=50,
    )
    level: int


class UpdateAccessLevelDTO(BaseModel):
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    level: int | None = None
    