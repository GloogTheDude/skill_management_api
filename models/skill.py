from sqlalchemy import String,Boolean,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Skill(Base):
    __tablename__ = "skill"

    id_skill: Mapped[int] = mapped_column(primary_key=True)
    name_skill: Mapped[str | None] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
                                            Boolean,
                                            default=False,
                                            server_default="false",
                                            nullable=False
                                        )
    id_domaine: Mapped[int] = mapped_column(
                            ForeignKey("domaine.id_domaine"),
                            nullable=False
                        )

    validations = relationship("SkillValidation", back_populates="skill")
    certification_links = relationship("CertificationSkill", back_populates="skill")
    diploma_links = relationship("DiplomaSkill", back_populates="skill")
    training_links = relationship("TrainingSkill", back_populates="skill")
    domaine = relationship("Domaine", back_populates="skills")
