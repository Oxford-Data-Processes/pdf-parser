from pydantic import BaseModel, Field
from typing import Optional, List, Union
from .shared_models import (
    DatetimeStr,
    DateStr,
    MonetaryAmount,
    Currency,
    IdStr,
    TransactionCategory,
    TransactionSubcategory,
)
from .document import DocumentType
from enum import Enum
from decimal import Decimal
from typing_extensions import Annotated
from .shared_models import CountryCode


class TransactionTypes(str, Enum):
    BGC = "BGC"  # Bank Giro Credit
    BP = "BP"  # Bill Payments
    CHG = "CHG"  # Charge
    CHQ = "CHQ"  # Cheque
    COR = "COR"  # Correction
    CPT = "CPT"  # Cashpoint
    DD = "DD"  # Direct Debit
    DEB = "DEB"  # Debit Card
    DEP = "DEP"  # Deposit
    FEE = "FEE"  # Fixed Service
    FPI = "FPI"  # Faster Payment In
    FPO = "FPO"  # Faster Payment Out
    MPI = "MPI"  # Mobile Payment In
    MPO = "MPO"  # Mobile Payment Out
    PAY = "PAY"  # Payment
    SO = "SO"  # Standing Order
    TFR = "TFR"  # Transfer


class Transaction(BaseModel):
    date: DateStr
    type: TransactionTypes
    amount: MonetaryAmount
    balance: Optional[MonetaryAmount] = None
    category: TransactionCategory
    confidence: Decimal = Field(..., decimal_places=2)
    description: str = Field(..., min_length=1, max_length=1000)
    subcategory: TransactionSubcategory


class CategorisedTransactions(BaseModel):
    income: List[Transaction]
    savings: List[Transaction]
    expenses: List[Transaction]


class MonthlyAverages(BaseModel):
    income: MonetaryAmount
    savings: MonetaryAmount
    expenses: MonetaryAmount


class Summary(BaseModel):
    total_income: MonetaryAmount
    total_savings: MonetaryAmount
    total_expenses: MonetaryAmount
    monthly_averages: MonthlyAverages


class AnalysisResults(BaseModel):
    summary: Summary
    categorised_transactions: CategorisedTransactions


SortCodeStr = Annotated[str, Field(pattern=r"^\d{2}-\d{2}-\d{2}$")]

RoutingNumberStr = Annotated[str, Field(pattern=r"^\d{9}$")]

BSBNumberStr = Annotated[str, Field(pattern=r"^\d{6}$")]

BicStr = Annotated[str, Field(pattern=r"^[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?$")]


class BankCodeType(str, Enum):
    SORT_CODE = "SORT_CODE"
    ROUTING_NUMBER = "ROUTING_NUMBER"
    BANK_STATE_BRANCH_NUMBER = "BANK_STATE_BRANCH_NUMBER"


class BankIdentifier(BaseModel):
    """International bank identification"""

    swift_bic: Optional[BicStr] = None
    local_bank_code: Optional[Union[SortCodeStr, RoutingNumberStr, BSBNumberStr]] = None
    local_bank_code_type: Optional[BankCodeType] = None


class AccountType(str, Enum):
    CURRENT = "CURRENT"
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEY_MARKET"
    INVESTMENT = "INVESTMENT"
    CREDIT = "CREDIT"
    OTHER = "OTHER"


class BankStatementData(BaseModel):
    type: DocumentType = DocumentType.BANK_STATEMENT
    """Generic international bank statement data"""

    bank_identifier: BankIdentifier
    account_type: Optional[AccountType] = None
    statement_period_start: Optional[DateStr] = None
    statement_period_end: Optional[DateStr] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None

    # Monetary amounts with currency
    start_balance: Optional[MonetaryAmount] = None
    end_balance: Optional[MonetaryAmount] = None
    total_money_in: Optional[MonetaryAmount] = None
    total_money_out: Optional[MonetaryAmount] = None
    overdraft_limit: Optional[MonetaryAmount] = None

    # Additional international fields
    iban: Optional[str] = None
    currency: Currency

    analysis_results: Optional[AnalysisResults] = None


class DeductionType(str, Enum):
    """Universal deduction types"""

    FEDERAL_INCOME_TAX = "FEDERAL_INCOME_TAX"
    STATE_INCOME_TAX = "STATE_INCOME_TAX"
    SOCIAL_SECURITY = "SOCIAL_SECURITY"
    PENSION = "PENSION"
    HEALTH_INSURANCE = "HEALTH_INSURANCE"
    OTHER = "OTHER"


class PayrollExemptionType(str, Enum):
    """Specific payroll exemption types"""

    PERSONAL_EXEMPTION = "PERSONAL_EXEMPTION"


class PayrollExemption(BaseModel):
    """Generic payroll exemption structure"""

    type: PayrollExemptionType
    amount: MonetaryAmount
    year_to_date: Optional[MonetaryAmount] = None
    description: Optional[str] = None


class PayrollDeduction(BaseModel):
    """Generic deduction structure"""

    type: DeductionType
    amount: MonetaryAmount
    year_to_date: Optional[MonetaryAmount] = None
    description: Optional[str] = None


class PayslipData(BaseModel):
    type: DocumentType = DocumentType.PAYSLIP
    """Generic international payslip data"""

    # Period information
    pay_period_start: Optional[DateStr] = None
    pay_period_end: Optional[DateStr] = None
    process_date: Optional[DateStr] = None

    # Employer information
    employer_name: Optional[str] = None
    employer_tax_id: Optional[str] = None
    employer_registration: Optional[str] = None  # Various business registration numbers

    # Employee information
    employee_id: Optional[str] = None
    tax_identifier: Optional[str] = None  # National Insurance Number, SSN, Tax ID etc.
    local_tax_code: Optional[str] = None  # Specific to country

    # Payment information
    currency: Currency
    gross_pay: MonetaryAmount
    net_pay: MonetaryAmount
    gross_ytd: Optional[MonetaryAmount] = None
    net_ytd: Optional[MonetaryAmount] = None

    # Deductions and contributions
    deductions: List[PayrollDeduction] = []

    exemptions: List[PayrollExemption] = []

    # Country-specific metadata
    country_code: CountryCode


class DocumentMetadata(BaseModel):
    id: IdStr
    document_id: IdStr
    document_type: DocumentType
    document_metadata: Union[BankStatementData, PayslipData]
    created_at: DatetimeStr
    updated_at: DatetimeStr
