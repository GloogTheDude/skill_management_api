from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EmployeeDeclaredSkill(Base):
    __tablename__ = "employee_declared_skill"
    __table_args__ = (
        UniqueConstraint("id_employee", "id_skill", name="uq_employee_declared_skill"),
        CheckConstraint("level BETWEEN 1 AND 5", name="ck_employee_declared_skill_level"),
    )

    id_employee_declared_skill: Mapped[int] = mapped_column(primary_key=True)
    id_employee: Mapped[int] = mapped_column(ForeignKey("employee.id_employee"), nullable=False)
    id_skill: Mapped[int] = mapped_column(ForeignKey("skill.id_skill"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    acquired_at: Mapped[date | None] = mapped_column(Date)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    employee = relationship("Employee", back_populates="declared_skills")
    skill = relationship("Skill", back_populates="declared_acquisitions")
