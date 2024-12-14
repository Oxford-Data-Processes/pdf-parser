from pydantic import BaseModel, Field
from typing import List, Annotated
from .shared_models import IdStr, DatetimeStr
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class DocumentType(str, Enum):
    BANK_STATEMENT = "BANK_STATEMENT"
    PAYSLIP = "PAYSLIP"
    UTILITY_BILL = "UTILITY_BILL"
    COUNCIL_TAX = "COUNCIL_TAX"
    MORTGAGE_STATEMENT = "MORTGAGE_STATEMENT"
    CREDIT_CARD_STATEMENT = "CREDIT_CARD_STATEMENT"
    INVESTMENT_STATEMENT = "INVESTMENT_STATEMENT"
    PENSION_STATEMENT = "PENSION_STATEMENT"
    TAX_DOCUMENT = "TAX_DOCUMENT"
    OTHER = "OTHER"


FilePathStr = Annotated[
    str, Field(max_length=255, pattern=r"\.(pdf|doc|docx|txt|jpg|jpeg|png)$")
]


class MimeType(str, Enum):
    PDF = "application/pdf"


class Document(BaseModel):
    id: IdStr
    client_id: IdStr
    name: FilePathStr
    document_type: str
    document_status: DocumentStatus
    file_path: FilePathStr
    file_size: int
    mime_type: MimeType
    validation_errors: List[str] = []
    created_at: DatetimeStr
    updated_at: DatetimeStr
