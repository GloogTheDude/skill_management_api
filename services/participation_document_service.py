from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import NoResultFound

from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_document_repository import ParticipationDocumentRepository
from db.repositories.participation_repository import ParticipationRepository
from dto.auth_dto import AuthEmployeeDTO
from dto.participation_document_dto import DocumentType, ResponseParticipationDocumentDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from models.participation_document import ParticipationDocument
from services.document_storage import LocalDocumentStorage
from services.employee_authorization_service import EmployeeAuthorizationService


class ParticipationDocumentService:
    def __init__(self, session, storage: LocalDocumentStorage | None = None):
        self.session = session
        self.storage = storage or LocalDocumentStorage()
        self.documents = ParticipationDocumentRepository(session)
        self.participations = ParticipationRepository(session)
        self.employees = EmployeeRepository(session)

    def _authorize(self, current: AuthEmployeeDTO, id_employee: int, id_training: int):
        participation = self.participations.get_one((id_employee, id_training))
        if participation.is_deleted:
            raise NoResultFound()
        employee = self.employees.get_one(id_employee)
        if employee.is_deleted:
            raise NoResultFound()
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current, employee)
        return participation, employee

    @staticmethod
    def _response(document):
        return ResponseParticipationDocumentDTO.model_validate(document, from_attributes=True)

    def list(self, current, id_employee, id_training):
        self._authorize(current, id_employee, id_training)
        return [self._response(item) for item in self.documents.get_for_participation(id_employee, id_training)]

    async def upload(self, current, id_employee, id_training, document_type: DocumentType, file: UploadFile):
        self._authorize(current, id_employee, id_training)
        if not file.filename or not file.filename.strip():
            raise ValueError("Filename is required.")
        if file.content_type not in self.storage.allowed_mime_types:
            raise ValueError("Unsupported document type.")
        # The upload is bounded before persistence; reading the spooled upload
        # directly also keeps this small service independent from an async
        # storage implementation.
        content = file.file.read(self.storage.max_size_bytes + 1)
        if len(content) > self.storage.max_size_bytes:
            raise ValueError("Document is too large.")
        extension = Path(file.filename).suffix.lower()
        storage_key = self.storage.save(content, extension)
        try:
            document = ParticipationDocument(
                id_employee=id_employee,
                id_training=id_training,
                document_type=document_type,
                original_filename=Path(file.filename).name,
                storage_key=storage_key,
                mime_type=file.content_type,
                size_bytes=len(content),
                uploaded_at=datetime.now(timezone.utc),
                id_uploaded_by=current.id_employee,
                is_deleted=False,
            )
            self.session.add(document)
            self.session.flush()
        except Exception:
            self.storage.resolve(storage_key).unlink(missing_ok=True)
            raise
        return self._response(document)

    def get_for_download(self, current, document_id: int):
        document = self.documents.get_active(document_id)
        if document is None:
            raise NoResultFound()
        self._authorize(current, document.id_employee, document.id_training)
        path = self.storage.resolve(document.storage_key)
        if not path.is_file():
            raise NoResultFound()
        return document, path

    def delete(self, current, document_id: int):
        EmployeeAuthorizationService.require_hr(current)
        document = self.documents.get_active(document_id)
        if document is None:
            raise NoResultFound()
        document.is_deleted = True
        self.session.flush()
