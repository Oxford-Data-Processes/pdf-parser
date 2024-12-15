import pytest
from datetime import datetime
from .document import (
    Document,
    DocumentStatus,
    DocumentType,
    MimeType,
    FilePathStr,
    ErrorType,
    Error,
)
from .shared_models import (
    IdStr,
    DatetimeStr,
    dump_json,
)


def test_create_valid_pdf_document():
    document = Document(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        name=FilePathStr("bank_statement.pdf"),
        document_type=DocumentType.BANK_STATEMENT,
        document_status=DocumentStatus.PENDING,
        file_path=FilePathStr("data/bank_statements/bank_statement.pdf"),
        file_size=1024,
        mime_type=MimeType.PDF,
        validation_errors=[],
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("document_valid_pdf", document)
    assert document.document_type == DocumentType.BANK_STATEMENT
    assert document.document_status == DocumentStatus.PENDING
    assert document.mime_type == MimeType.PDF
    assert document.file_size == 1024
    assert len(document.validation_errors) == 0


def test_create_valid_document_with_errors():
    document = Document(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        name=FilePathStr("payslip.pdf"),
        document_type=DocumentType.PAYSLIP,
        document_status=DocumentStatus.ERROR,
        file_path=FilePathStr("data/payslips/payslip.pdf"),
        file_size=2048,
        mime_type=MimeType.PDF,
        validation_errors=[
            Error(type=ErrorType.INVALID_DATE_FORMAT, message="Invalid date format"),
            Error(
                type=ErrorType.MISSING_REQUIRED_FIELD, message="Missing required field"
            ),
        ],
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("document_with_errors", document)
    assert document.document_type == DocumentType.PAYSLIP
    assert document.document_status == DocumentStatus.ERROR
    assert len(document.validation_errors) == 2
    assert any(
        error.message == "Invalid date format" for error in document.validation_errors
    )
    assert any(
        error.message == "Missing required field"
        for error in document.validation_errors
    )
    assert any(
        error.type == ErrorType.INVALID_DATE_FORMAT
        for error in document.validation_errors
    )
    assert any(
        error.type == ErrorType.MISSING_REQUIRED_FIELD
        for error in document.validation_errors
    )


def test_create_valid_processed_document():
    document = Document(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        name=FilePathStr("utility_bill.pdf"),
        document_type=DocumentType.UTILITY_BILL,
        document_status=DocumentStatus.PROCESSED,
        file_path=FilePathStr("data/utility_bills/utility_bill.pdf"),
        file_size=3072,
        mime_type=MimeType.PDF,
        validation_errors=[],
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("document_processed", document)
    assert document.document_type == DocumentType.UTILITY_BILL
    assert document.document_status == DocumentStatus.PROCESSED
    assert document.file_size == 3072
    assert len(document.validation_errors) == 0


def test_invalid_file_path():
    with pytest.raises(ValueError):
        Document(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            name=FilePathStr("document.txt"),
            document_type=DocumentType.OTHER,
            document_status=DocumentStatus.PENDING,
            file_path=FilePathStr("invalid_extension.xyz"),  # Invalid file extension
            file_size=1024,
            mime_type=MimeType.PDF,
            validation_errors=[],
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_document_status():
    with pytest.raises(ValueError):
        Document(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            name=FilePathStr("document.pdf"),
            document_type=DocumentType.OTHER,
            document_status="INVALID_STATUS",  # Invalid status
            file_path=FilePathStr("data/documents/document.pdf"),
            file_size=1024,
            mime_type=MimeType.PDF,
            validation_errors=[],
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_mime_type():
    with pytest.raises(ValueError):
        Document(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            name=FilePathStr("document.pdf"),
            document_type=DocumentType.OTHER,
            document_status=DocumentStatus.PENDING,
            file_path=FilePathStr("data/documents/document.pdf"),
            file_size=1024,
            mime_type="invalid/mime",  # Invalid MIME type
            validation_errors=[],
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_negative_file_size():
    with pytest.raises(ValueError):
        Document(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            name=FilePathStr("document.pdf"),
            document_type=DocumentType.OTHER,
            document_status=DocumentStatus.PENDING,
            file_path=FilePathStr("data/documents/document.pdf"),
            file_size=-1,  # Negative file size
            mime_type=MimeType.PDF,
            validation_errors=[],
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )
