from sqlalchemy import ForeignKey, String,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Employee(Base):
    __tablename__ = "employee"

    id_employee: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    hash_password: Mapped[str | None] = mapped_column(String(255))
    mail: Mapped[str | None] = mapped_column(String(50))
    is_deleted: Mapped[bool] = mapped_column(
                                    Boolean,
                                    default=False,
                                    server_default="false",
                                    nullable=False
                                )


    id_role: Mapped[int] = mapped_column(ForeignKey("role.id_role"))
    id_manager: Mapped[int | None] = mapped_column(
        ForeignKey("employee.id_employee"),
        nullable=True,
    )

    role = relationship("Role", back_populates="employees")

    manager = relationship(
        "Employee",
        remote_side=[id_employee],
        back_populates="managed_employees",
    )
    managed_employees = relationship(
        "Employee",
        back_populates="manager",
    )

    skill_validations_received = relationship(
        "SkillValidation",
        foreign_keys="SkillValidation.id_employee",
        back_populates="employee",
    )
    skill_validations_validated = relationship(
        "SkillValidation",
        foreign_keys="SkillValidation.id_validator",
        back_populates="validator",
    )

    training_requests = relationship(
        "TrainingRequest",
        foreign_keys="TrainingRequest.id_employee",
        back_populates="employee",
    )
    training_requests_validated = relationship(
        "TrainingRequest",
        foreign_keys="TrainingRequest.id_validator",
        back_populates="validator",
    )

    diplomas = relationship("EmployeeDiploma", back_populates="employee")
    certifications = relationship("EmployeeCertification", back_populates="employee")
    participations = relationship("Participation", back_populates="employee")
