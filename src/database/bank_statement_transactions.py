from pydantic import BaseModel

from database.document_metadata import TransactionCategory, TransactionSubcategory
from database.shared_models import IdStr, MonetaryAmount, Currency, DateStr, DatetimeStr


class BankStatementTransaction(BaseModel):
    id: IdStr
    client_id: IdStr
    document_id: IdStr
    amount: MonetaryAmount
    currency: Currency
    description: str
    date: DateStr
    category: TransactionCategory
    subcategory: TransactionSubcategory
    created_at: DatetimeStr
    updated_at: DatetimeStr
