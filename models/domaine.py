from sqlalchemy import String,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Domaine(Base):
    __tablename__ = "domaine"

    id_domaine: Mapped[int] = mapped_column(primary_key=True)
    nom_domaine: Mapped[str] = mapped_column(String(50))
    is_deleted: Mapped[bool] = mapped_column(
                                            Boolean,
                                            default=False,
                                            server_default="false",
                                            nullable=False
                                        )

    diplomas = relationship("Diploma", back_populates="domaine")
    certifications = relationship("Certification", back_populates="domaine")
    trainings = relationship("Training", back_populates="domaine")
    skills = relationship("Skill",back_populates="domaine")
