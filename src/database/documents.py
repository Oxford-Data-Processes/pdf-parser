from pydantic import BaseModel, constr, Field
from typing import List
from shared_models import Id, Datetime
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class DocumentType(str, Enum):
    MORTGAGE_APPLICATION = "MORTGAGE_APPLICATION"
    BANK_STATEMENT = "BANK_STATEMENT"
    PAY_STUB = "PAY_STUB"
    TAX_RETURN = "TAX_RETURN"
    ID_DOCUMENT = "ID_DOCUMENT"
    OTHER = "OTHER"


class FilePath(constr):
    __root__: str = Field(
        ..., max_length=255, regex=r"\.(pdf|doc|docx|txt|jpg|jpeg|png)$"
    )


class MimeType(Enum):
    PDF = "application/pdf"


class Document(BaseModel):
    id: Id
    client_id: Id
    name: FilePath
    document_type: str
    document_status: DocumentStatus
    file_path: FilePath
    file_size: int
    mime_type: MimeType
    validation_errors: List[str] = []
    created_at: Datetime
    updated_at: Datetime
