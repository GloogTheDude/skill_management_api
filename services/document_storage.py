import os
from pathlib import Path
from uuid import uuid4


class LocalDocumentStorage:
    allowed_mime_types = {"application/pdf", "image/jpeg", "image/png"}
    max_size_bytes = 10 * 1024 * 1024

    def __init__(self, root: str | None = None):
        self.root = Path(root or os.getenv(
            "PARTICIPATION_DOCUMENT_STORAGE_DIR",
            "storage/participation_documents",
        )).resolve()

    def save(self, content: bytes, extension: str) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        key = f"participations/{uuid4().hex}{extension}"
        path = self.root / key.split("/", 1)[1]
        path.write_bytes(content)
        return key

    def resolve(self, storage_key: str) -> Path:
        if not storage_key.startswith("participations/") or ".." in Path(storage_key).parts:
            raise ValueError("Invalid storage key")
        path = (self.root / storage_key.split("/", 1)[1]).resolve()
        if self.root not in path.parents:
            raise ValueError("Invalid storage key")
        return path
