from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union
from .shared_models import DatetimeStr, DateStr, MonetaryAmount, Currency
from .documents import DocumentType
from enum import Enum
from decimal import Decimal
from typing_extensions import Annotated


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


class TransactionCategory(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFERS = "TRANSFERS"
    HEALTHCARE = "HEALTHCARE"
    TRANSPORT = "TRANSPORT"
    FOOD = "FOOD"
    HOUSING = "HOUSING"
    SHOPPING = "SHOPPING"
    MISCELLANEOUS = "MISCELLANEOUS"
    DIGITAL_SERVICES = "DIGITAL_SERVICES"
    ENTERTAINMENT = "ENTERTAINMENT"
    UNCATEGORISED = "UNCATEGORISED"


class TransactionSubcategory(str, Enum):
    # Transfer subcategories
    AUTOMATED_SAVINGS = "AUTOMATED_SAVINGS"
    BANK_TRANSFER = "BANK_TRANSFER"

    # Income subcategories
    SALARY = "SALARY"
    REFUND = "REFUND"
    PERSONAL_TRANSFER = "PERSONAL_TRANSFER"

    # Healthcare subcategories
    FITNESS = "FITNESS"

    # Transport subcategories
    CAR = "CAR"
    PUBLIC = "PUBLIC"
    MICROMOBILITY = "MICROMOBILITY"

    # Food subcategories
    GROCERIES = "GROCERIES"
    TAKEAWAY = "TAKEAWAY"
    DINING_OUT = "DINING_OUT"

    # Housing subcategories
    UTILITIES = "UTILITIES"
    RENT = "RENT"
    MORTGAGE = "MORTGAGE"
    INSURANCE = "INSURANCE"
    MAINTENANCE = "MAINTENANCE"

    # Shopping subcategories
    ONLINE_RETAIL = "ONLINE_RETAIL"
    IN_STORE_RETAIL = "IN_STORE_RETAIL"
    CLOTHING = "CLOTHING"
    ELECTRONICS = "ELECTRONICS"

    # Miscellaneous subcategories
    CASH = "CASH"
    FEES = "FEES"

    # Digital services subcategories
    SUBSCRIPTIONS = "SUBSCRIPTIONS"
    SOFTWARE = "SOFTWARE"
    STREAMING = "STREAMING"

    # Entertainment subcategories
    ACTIVITIES = "ACTIVITIES"
    EVENTS = "EVENTS"
    HOBBIES = "HOBBIES"

    # Personal subcategories
    CARE = "CARE"
    EDUCATION = "EDUCATION"
    GIFTS = "GIFTS"

    OTHER = "OTHER"


class Transaction(BaseModel):
    date: DateStr
    type: TransactionTypes
    amount: MonetaryAmount
    balance: Optional[MonetaryAmount] = None
    category: TransactionCategory
    confidence: Decimal = Field(..., decimal_places=2)
    description: str
    subcategory: TransactionSubcategory


class CategorisedTransactions(BaseModel):
    income: Dict[str, List[Transaction]]
    savings: Dict[str, List[Transaction]]
    expenses: Dict[str, List[Transaction]]


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
    BSB = "BSB"


class BankIdentifier(BaseModel):
    """International bank identification"""

    swift_bic: Optional[BicStr] = None
    local_bank_code: Optional[Union[SortCodeStr, RoutingNumberStr, BSBNumberStr]] = None
    local_bank_code_type: Optional[BankCodeType] = None


class AccountType(str, Enum):
    CHECKING = "CHECKING"  # US/International
    CURRENT = "CURRENT"  # UK
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEY_MARKET"
    INVESTMENT = "INVESTMENT"
    CREDIT = "CREDIT"
    OTHER = "OTHER"


class ExchangeRate(BaseModel):
    from_currency: Currency
    to_currency: Currency
    rate: Decimal = Field(..., decimal_places=5)


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
    exchange_rates: Optional[List[ExchangeRate]] = None

    analysis_results: Optional[AnalysisResults] = None


class TaxSystem(str, Enum):
    """Different tax systems"""

    UK = "UK"  # National Insurance, PAYE
    US = "US"  # Social Security, Medicare
    EU = "EU"  # Social Security variations
    OTHER = "OTHER"


class DeductionType(str, Enum):
    """Universal deduction types"""

    TAX = "TAX"  # Generic income tax
    SOCIAL_SECURITY = "SOCIAL_SECURITY"  # NI, Social Security, etc.
    PENSION = "PENSION"
    HEALTH_INSURANCE = "HEALTH_INSURANCE"
    OTHER = "OTHER"


class PayrollDeduction(BaseModel):
    """Generic deduction structure"""

    type: DeductionType
    amount: MonetaryAmount
    year_to_date: Optional[MonetaryAmount] = None
    description: Optional[str] = None
    local_type: Optional[str] = None  # e.g., "National Insurance", "Medicare"


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

    # Country-specific metadata
    tax_system: TaxSystem
    country_code: str = Field(..., pattern=r"^[A-Z]{2}$")  # ISO 3166-1 alpha-2

    # Additional fields
    payment_method: Optional[str] = None


class DocumentMetadata(BaseModel):
    id: str
    document_id: str
    document_type: DocumentType
    document_metadata: Union[BankStatementData, PayslipData]
    created_at: DatetimeStr
    updated_at: DatetimeStr
