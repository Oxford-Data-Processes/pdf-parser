from pydantic import BaseModel
from typing import List


class Metadata(BaseModel):
    document_id: str
    parsed_at: str
    number_of_pages: int


class Transaction(BaseModel):
    table_header: str
    data: List[dict]


class Table(BaseModel):
    table_header: str
    data: List[Transaction]


class Page(BaseModel):
    forms: dict
    tables: List[Table]


class Document(BaseModel):
    metadata: Metadata
    pages: List[Page]
