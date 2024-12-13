from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from shared_models import Datetime
from documents import DocumentType


class Transaction(BaseModel):
    date: str
    type: str
    amount: float
    balance: Optional[float] = None
    category: str
    confidence: float
    description: str
    subcategory: str


class CategorizedTransactions(BaseModel):
    income: Dict[str, List[Transaction]]
    savings: Dict[str, List[Transaction]]
    expenses: Dict[str, List[Transaction]]


class AnalysisResults(BaseModel):
    summary: Dict[str, Any]
    categorized_transactions: CategorizedTransactions


class BankStatementData(BaseModel):
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None
    account_type: Optional[str] = None
    statement_period: Optional[str] = None
    sort_code: Optional[str] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None
    end_balance: Optional[float] = None
    start_balance: Optional[float] = None
    total_money_in: Optional[float] = None
    overdraft_limit: Optional[float] = None
    total_money_out: Optional[float] = None
    analysis_results: Optional[AnalysisResults] = None


class PayStubData(BaseModel):
    pay_period: Optional[str] = None
    pay_date: Optional[str] = None
    pay_amount: Optional[float] = None
    pay_rate: Optional[float] = None
    pay_period_start: Optional[str] = None
    pay_period_end: Optional[str] = None


class DocumentMetadata(BaseModel):
    id: str
    document_id: str
    document_type: DocumentType
    document_metadata: Union[BankStatementData, PayStubData]
    created_at: Datetime
    updated_at: Datetime
