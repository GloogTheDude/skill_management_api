from datetime import datetime
from typing import Literal

from pydantic import BaseModel


DocumentType = Literal["CERTIFICATE", "DIPLOMA", "ATTENDANCE_CERTIFICATE", "OTHER"]


class ResponseParticipationDocumentDTO(BaseModel):
    id_participation_document: int
    id_employee: int
    id_training: int
    document_type: DocumentType
    original_filename: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime
    id_uploaded_by: int
