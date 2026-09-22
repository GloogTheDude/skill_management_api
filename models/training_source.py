from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class TrainingSource(Base):
    __tablename__ = "training_source"

    id_source: Mapped[int] = mapped_column(primary_key=True)
    name_source: Mapped[str] = mapped_column(String(50))
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False
    )

    trainings = relationship("Training", back_populates="source")