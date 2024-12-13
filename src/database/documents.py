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
    MORTGAGE_APPLICATION = "Mortgage Application"
    BANK_STATEMENT = "Bank Statement"
    PAY_STUB = "Pay Stub"
    TAX_RETURN = "Tax Return"
    ID_DOCUMENT = "ID Document"
    OTHER = "Other"


class PDFName(constr):
    __root__: str = Field(..., max_length=255, regex=r"\.pdf$")


class Document(BaseModel):
    id: Id
    client_id: Id
    name: PDFName
    type: str
    status: DocumentStatus
    file_path: str
    file_size: int
    mime_type: str
    validation_errors: List[str] = []
    created_at: Datetime
    updated_at: Datetime
