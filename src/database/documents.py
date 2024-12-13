from pydantic import BaseModel
from typing import List
from shared_models import Id, Datetime
from enum import Enum


class DocumentStatus(str, Enum):
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Document(BaseModel):
    id: Id
    client_id: Id
    name: str
    type: str
    status: DocumentStatus
    file_path: str
    file_size: int
    mime_type: str
    validation_errors: List[str] = []
    created_at: Datetime
    updated_at: Datetime
