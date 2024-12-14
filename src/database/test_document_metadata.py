import pytest
from datetime import datetime
from decimal import Decimal
from .document_metadata import (
    Transaction,
    TransactionTypes,
    TransactionCategory,
    TransactionSubcategory,
    CategorisedTransactions,
    MonthlyAverages,
    Summary,
    AnalysisResults,
    BankIdentifier,
    AccountType,
    BankStatementData,
    DeductionType,
    PayrollDeduction,
    PayslipData,
    DocumentMetadata,
    DocumentType,
    BankCodeType,
    SortCodeStr,
    BicStr,
)
from .shared_models import (
    MonetaryAmount,
    Currency,
    DateStr,
    DatetimeStr,
    IdStr,
    dump_json,
    CountryCode,
)


def test_create_valid_transaction():
    transaction = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=100000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.SALARY,
        confidence=Decimal("0.95"),
        description="Salary payment",
    )
    assert transaction.type == TransactionTypes.FPI
    assert transaction.category == TransactionCategory.INCOME
    assert transaction.subcategory == TransactionSubcategory.SALARY
    assert transaction.amount.amount == 100000
    assert transaction.balance.amount == 500000
    assert transaction.confidence == Decimal("0.95")


def test_create_valid_categorised_transactions():
    salary_transaction = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=100000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.SALARY,
        confidence=Decimal("0.95"),
        description="Salary payment",
    )

    rent_transaction = Transaction(
        date=DateStr("2023-12-02"),
        type=TransactionTypes.DD,
        amount=MonetaryAmount(amount=150000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=350000, currency=Currency.GBP),
        category=TransactionCategory.HOUSING,
        subcategory=TransactionSubcategory.RENT,
        confidence=Decimal("0.98"),
        description="Monthly rent",
    )

    savings_transaction = Transaction(
        date=DateStr("2023-12-03"),
        type=TransactionTypes.TFR,
        amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=300000, currency=Currency.GBP),
        category=TransactionCategory.TRANSFERS,
        subcategory=TransactionSubcategory.AUTOMATED_SAVINGS,
        confidence=Decimal("0.99"),
        description="Monthly savings",
    )

    categorised = CategorisedTransactions(
        income=[salary_transaction],
        savings=[savings_transaction],
        expenses=[rent_transaction],
    )
    assert len(categorised.income) == 1
    assert len(categorised.savings) == 1
    assert len(categorised.expenses) == 1


def test_create_valid_monthly_averages():
    averages = MonthlyAverages(
        income=MonetaryAmount(amount=100000, currency=Currency.GBP),
        savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        expenses=MonetaryAmount(amount=150000, currency=Currency.GBP),
    )
    assert averages.income.amount == 100000
    assert averages.savings.amount == 50000
    assert averages.expenses.amount == 150000


def test_create_valid_bank_statement_data():
    bank_statement = BankStatementData(
        type=DocumentType.BANK_STATEMENT,
        bank_identifier=BankIdentifier(
            swift_bic=BicStr("NWBKGB2L"),
            local_bank_code=SortCodeStr("12-34-56"),
            local_bank_code_type=BankCodeType.SORT_CODE,
        ),
        account_type=AccountType.CURRENT,
        statement_period_start=DateStr("2023-12-01"),
        statement_period_end=DateStr("2023-12-31"),
        account_number="12345678",
        account_holder="John Doe",
        start_balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        end_balance=MonetaryAmount(amount=450000, currency=Currency.GBP),
        total_money_in=MonetaryAmount(amount=100000, currency=Currency.GBP),
        total_money_out=MonetaryAmount(amount=150000, currency=Currency.GBP),
        overdraft_limit=MonetaryAmount(amount=200000, currency=Currency.GBP),
        currency=Currency.GBP,
    )
    assert bank_statement.type == DocumentType.BANK_STATEMENT
    assert bank_statement.bank_identifier.swift_bic == "NWBKGB2L"
    assert bank_statement.account_type == AccountType.CURRENT
    assert bank_statement.currency == Currency.GBP


def test_create_valid_payslip_data():
    payslip = PayslipData(
        type=DocumentType.PAYSLIP,
        employer_name="ACME Corp",
        employer_tax_id="123/AB456",
        employee_id="EMP123",
        tax_identifier="AB123456C",
        local_tax_code="1250L",
        currency=Currency.GBP,
        gross_pay=MonetaryAmount(amount=300000, currency=Currency.GBP),
        net_pay=MonetaryAmount(amount=240000, currency=Currency.GBP),
        gross_ytd=MonetaryAmount(amount=2700000, currency=Currency.GBP),
        net_ytd=MonetaryAmount(amount=2160000, currency=Currency.GBP),
        deductions=[
            PayrollDeduction(
                type=DeductionType.FEDERAL_INCOME_TAX,
                amount=MonetaryAmount(amount=40000, currency=Currency.GBP),
                year_to_date=MonetaryAmount(amount=360000, currency=Currency.GBP),
                description="Income Tax",
            ),
            PayrollDeduction(
                type=DeductionType.SOCIAL_SECURITY,
                amount=MonetaryAmount(amount=20000, currency=Currency.GBP),
                year_to_date=MonetaryAmount(amount=180000, currency=Currency.GBP),
                description="National Insurance",
            ),
        ],
        country_code=CountryCode.GB,
        pay_period_start=DateStr("2023-12-01"),
        pay_period_end=DateStr("2023-12-31"),
        process_date=DateStr("2023-12-31"),
    )
    assert payslip.type == DocumentType.PAYSLIP
    assert payslip.country_code == CountryCode.GB
    assert len(payslip.deductions) == 2
    assert payslip.gross_pay.amount == 300000
    assert payslip.net_pay.amount == 240000


def test_create_valid_document_metadata():
    payslip = PayslipData(
        type=DocumentType.PAYSLIP,
        employer_name="ACME Corp",
        employer_tax_id="123/AB456",
        employee_id="EMP123",
        tax_identifier="AB123456C",
        local_tax_code="1250L",
        currency=Currency.GBP,
        gross_pay=MonetaryAmount(amount=300000, currency=Currency.GBP),
        net_pay=MonetaryAmount(amount=240000, currency=Currency.GBP),
        gross_ytd=MonetaryAmount(amount=2700000, currency=Currency.GBP),
        net_ytd=MonetaryAmount(amount=2160000, currency=Currency.GBP),
        deductions=[
            PayrollDeduction(
                type=DeductionType.FEDERAL_INCOME_TAX,
                amount=MonetaryAmount(amount=40000, currency=Currency.GBP),
                description="Income Tax",
            ),
        ],
        country_code=CountryCode.GB,
        pay_period_start=DateStr("2023-12-01"),
        pay_period_end=DateStr("2023-12-31"),
    )

    metadata = DocumentMetadata(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        document_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        document_type=DocumentType.PAYSLIP,
        document_metadata=payslip,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("document_metadata_payslip", metadata)
    assert metadata.document_type == DocumentType.PAYSLIP
    assert isinstance(metadata.document_metadata, PayslipData)


def test_create_valid_document_metadata_bank_statement():
    # Create sample transactions
    salary = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=500000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.SALARY,
        confidence=Decimal("0.95"),
        description="ACME CORP SALARY",
    )

    rent = Transaction(
        date=DateStr("2023-12-02"),
        type=TransactionTypes.DD,
        amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=300000, currency=Currency.GBP),
        category=TransactionCategory.HOUSING,
        subcategory=TransactionSubcategory.RENT,
        confidence=Decimal("0.98"),
        description="LANDLORD RENT PAYMENT",
    )

    savings = Transaction(
        date=DateStr("2023-12-03"),
        type=TransactionTypes.TFR,
        amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=250000, currency=Currency.GBP),
        category=TransactionCategory.TRANSFERS,
        subcategory=TransactionSubcategory.AUTOMATED_SAVINGS,
        confidence=Decimal("0.99"),
        description="TRANSFER TO SAVINGS",
    )

    # Create categorised transactions
    categorised = CategorisedTransactions(
        income=[salary],
        expenses=[rent],
        savings=[savings],
    )

    # Create monthly averages
    averages = MonthlyAverages(
        income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        expenses=MonetaryAmount(amount=200000, currency=Currency.GBP),
    )

    # Create summary
    summary = Summary(
        total_income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        total_savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        total_expenses=MonetaryAmount(amount=200000, currency=Currency.GBP),
        monthly_averages=averages,
    )

    # Create analysis results
    analysis = AnalysisResults(
        summary=summary,
        categorised_transactions=categorised,
    )

    bank_statement = BankStatementData(
        type=DocumentType.BANK_STATEMENT,
        bank_identifier=BankIdentifier(
            swift_bic=BicStr("NWBKGB2L"),
            local_bank_code=SortCodeStr("12-34-56"),
            local_bank_code_type=BankCodeType.SORT_CODE,
        ),
        account_type=AccountType.CURRENT,
        statement_period_start=DateStr("2023-12-01"),
        statement_period_end=DateStr("2023-12-31"),
        account_number="12345678",
        account_holder="John Doe",
        start_balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        end_balance=MonetaryAmount(amount=250000, currency=Currency.GBP),
        total_money_in=MonetaryAmount(amount=500000, currency=Currency.GBP),
        total_money_out=MonetaryAmount(amount=250000, currency=Currency.GBP),
        overdraft_limit=MonetaryAmount(amount=200000, currency=Currency.GBP),
        currency=Currency.GBP,
        analysis_results=analysis,
    )

    metadata = DocumentMetadata(
        id=IdStr("123e4567-e89b-12d3-a456-426614174001"),
        document_id=IdStr("987fcdeb-51a2-43d7-9012-345678901235"),
        document_type=DocumentType.BANK_STATEMENT,
        document_metadata=bank_statement,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("document_metadata_bank_statement", metadata)

    # Basic metadata assertions
    assert metadata.document_type == DocumentType.BANK_STATEMENT
    assert isinstance(metadata.document_metadata, BankStatementData)
    assert metadata.document_metadata.bank_identifier.swift_bic == "NWBKGB2L"
    assert metadata.document_metadata.account_type == AccountType.CURRENT
    assert metadata.document_metadata.currency == Currency.GBP

    # Analysis results assertions
    analysis_results = metadata.document_metadata.analysis_results
    assert analysis_results is not None
    assert len(analysis_results.categorised_transactions.income) == 1
    assert len(analysis_results.categorised_transactions.expenses) == 1
    assert len(analysis_results.categorised_transactions.savings) == 1
    assert analysis_results.summary.total_income.amount == 500000
    assert analysis_results.summary.total_expenses.amount == 200000
    assert analysis_results.summary.total_savings.amount == 50000
    assert (
        analysis_results.categorised_transactions.income[0].subcategory
        == TransactionSubcategory.SALARY
    )
    assert (
        analysis_results.categorised_transactions.expenses[0].subcategory
        == TransactionSubcategory.RENT
    )
    assert (
        analysis_results.categorised_transactions.savings[0].subcategory
        == TransactionSubcategory.AUTOMATED_SAVINGS
    )


def test_invalid_swift_bic():
    with pytest.raises(ValueError):
        BankIdentifier(
            swift_bic=BicStr("INVALID"),
            local_bank_code=SortCodeStr("12-34-56"),
            local_bank_code_type=BankCodeType.SORT_CODE,
        )


def test_invalid_country_code():
    with pytest.raises(ValueError):
        PayslipData(
            type=DocumentType.PAYSLIP,
            employer_name="ACME Corp",
            currency=Currency.GBP,
            gross_pay=MonetaryAmount(amount=300000, currency=Currency.GBP),
            net_pay=MonetaryAmount(amount=240000, currency=Currency.GBP),
            country_code="INVALID",
        )
