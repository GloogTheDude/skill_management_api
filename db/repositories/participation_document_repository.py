from sqlalchemy import select

from db.repositories.base_repository import BaseRepository
from models.participation_document import ParticipationDocument


class ParticipationDocumentRepository(BaseRepository[ParticipationDocument]):
    model = ParticipationDocument

    def get_for_participation(self, id_employee: int, id_training: int):
        stmt = select(ParticipationDocument).where(
            ParticipationDocument.id_employee == id_employee,
            ParticipationDocument.id_training == id_training,
            ParticipationDocument.is_deleted.is_(False),
        ).order_by(ParticipationDocument.uploaded_at)
        return list(self._session.scalars(stmt).all())

    def get_active(self, document_id: int):
        document = self._session.get(ParticipationDocument, document_id)
        if document is None or document.is_deleted:
            return None
        return document
