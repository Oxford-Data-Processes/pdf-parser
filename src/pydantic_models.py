from pydantic import BaseModel, RootModel
from typing import List, Optional, Dict, Any


class Metadata(BaseModel):
    document_id: str
    parsed_at: str
    number_of_pages: int


class Table(BaseModel):
    data: List[RootModel]


class Page(BaseModel):
    forms: Optional[List[RootModel]]
    tables: Optional[List[Table]]


class Document(BaseModel):
    metadata: Metadata
    pages: List[Page]
