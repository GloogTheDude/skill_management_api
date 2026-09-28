from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Training(Base):
    __tablename__ = "training"

    __table_args__ = (
        CheckConstraint(
            "NOT (id_certification IS NOT NULL AND id_diploma IS NOT NULL)",
            name="chk_training_only_one_main_target",
        ),
    )

    id_training: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str | None] = mapped_column(String(50))

    id_domaine: Mapped[int | None] = mapped_column(
        ForeignKey("domaine.id_domaine"),
        nullable=True,
    )

    id_source: Mapped[int | None] = mapped_column(
        ForeignKey("training_source.id_source"),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    id_certification: Mapped[int | None] = mapped_column(
        ForeignKey("certification.id_certification"),
        nullable=True,
    )

    id_diploma: Mapped[int | None] = mapped_column(
        ForeignKey("diploma.id_diploma"),
        nullable=True,
    )

    start_: Mapped[date | None] = mapped_column(Date)
    end_: Mapped[date | None] = mapped_column(Date)

    cost_hour: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    duration_hours: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    domaine = relationship("Domaine", back_populates="trainings")
    source = relationship("TrainingSource", back_populates="trainings")

    certification = relationship("Certification", back_populates="trainings")
    diploma = relationship("Diploma", back_populates="trainings")

    requests = relationship("TrainingRequest", back_populates="training")
    participations = relationship("Participation", back_populates="training")
    skill_links = relationship("TrainingSkill", back_populates="training")
