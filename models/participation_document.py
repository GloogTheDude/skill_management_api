from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, ForeignKeyConstraint, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ParticipationDocument(Base):
    __tablename__ = "participation_document"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_employee", "id_training"],
            ["participation.id_employee", "participation.id_training"],
        ),
    )

    id_participation_document: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_employee: Mapped[int] = mapped_column(nullable=False)
    id_training: Mapped[int] = mapped_column(nullable=False)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    id_uploaded_by: Mapped[int] = mapped_column(ForeignKey("employee.id_employee"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    participation = relationship("Participation", back_populates="documents")
    uploaded_by = relationship("Employee", foreign_keys=[id_uploaded_by])
