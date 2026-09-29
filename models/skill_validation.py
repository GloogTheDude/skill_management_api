from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Boolean, String, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SkillValidation(Base):
    __tablename__ = "skill_validation"
    __table_args__ = (
        Index(
            "uq_skill_validation_current_employee_skill",
            "id_employee",
            "id_skill",
            unique=True,
            postgresql_where=text("superseded_at IS NULL AND is_deleted = false"),
            sqlite_where=text("superseded_at IS NULL AND is_deleted = 0"),
        ),
    )

    id_skill_validation: Mapped[int] = mapped_column(primary_key=True)
    date_: Mapped[date | None] = mapped_column(Date)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    justification: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    level_skill: Mapped[int | None]

    id_validation: Mapped[int] = mapped_column(ForeignKey("validation_type.id_validation"))
    id_employee: Mapped[int] = mapped_column(ForeignKey("employee.id_employee"))
    id_validator: Mapped[int] = mapped_column(ForeignKey("employee.id_employee"))
    id_skill: Mapped[int] = mapped_column(ForeignKey("skill.id_skill"))
    is_deleted: Mapped[bool] = mapped_column(
                                            Boolean,
                                            default=False,
                                            server_default="false",
                                            nullable=False
                                        )

    validation_type = relationship("ValidationType", back_populates="skill_validations")
    employee = relationship(
        "Employee",
        foreign_keys=[id_employee],
        back_populates="skill_validations_received",
    )
    validator = relationship(
        "Employee",
        foreign_keys=[id_validator],
        back_populates="skill_validations_validated",
    )
    skill = relationship("Skill", back_populates="validations")
