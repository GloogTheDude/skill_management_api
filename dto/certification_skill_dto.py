from pydantic import BaseModel, Field

from models.certification_skill import CertificationSkill


class ResponseCertificationSkillDTO(BaseModel):
    id_certification: int
    id_skill: int
    granted_level: int | None
    certification_name: str | None
    skill_name: str

    @classmethod
    def from_entity(
        cls,
        certification_skill: CertificationSkill,
    ):
        return cls(
            id_certification=certification_skill.id_certification,
            id_skill=certification_skill.id_skill,
            granted_level=certification_skill.granted_level,
            certification_name=certification_skill.certification.subject_certification,
            skill_name=certification_skill.skill.name_skill,
        )


class CreateCertificationSkillDTO(BaseModel):
    id_certification: int = Field(gt=0)
    id_skill: int = Field(gt=0)
    granted_level: int | None = None


class UpdateCertificationSkillDTO(BaseModel):
    granted_level: int | None = None