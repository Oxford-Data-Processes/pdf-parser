import pytest
from datetime import datetime
from decimal import Decimal
from typing import List
from .documentmetadata import (
    DocumentMetadata,
    DocumentType,
    Transaction,
    TransactionTypes,
    CategorisedTransactions,
    BankStatementData,
    PayslipData,
    BankIdentifier,
    BankCodeType,
    AccountType,
    PayrollDeduction,
    PayrollExemption,
    PayrollExemptionType,
    DeductionType,
    AnalysisResults,
    Summary,
    MonthlyAverages,
)
from .shared_models import (
    MonetaryAmount,
    Currency,
    DateStr,
    DatetimeStr,
    IdStr,
    TransactionCategory,
    TransactionSubcategory,
    CountryCode,
    dump_json,
)


def test_create_valid_transaction():
    transaction = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=100000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.INCOME_WAGES,
        confidence=Decimal("0.95"),
        description="Salary payment",
    )
    assert transaction.date == "2023-12-01"
    assert transaction.amount.amount == 100000
    assert transaction.category == TransactionCategory.INCOME
    assert transaction.subcategory == TransactionSubcategory.INCOME_WAGES


def test_create_valid_categorised_transactions():
    salary_transaction = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=100000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.INCOME_WAGES,
        confidence=Decimal("0.95"),
        description="Salary payment",
    )
    categorised = CategorisedTransactions(
        income=[salary_transaction],
        expenses=[],
        savings=[],
    )
    assert len(categorised.income) == 1
    assert len(categorised.expenses) == 0
    assert len(categorised.savings) == 0
    assert categorised.income[0].category == TransactionCategory.INCOME
    assert categorised.income[0].subcategory == TransactionSubcategory.INCOME_WAGES


def test_create_valid_bank_statement_data():
    # Create sample transactions for analysis results
    salary = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=500000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.INCOME_WAGES,
        confidence=Decimal("0.95"),
        description="ACME CORP SALARY",
    )

    monthly_averages = MonthlyAverages(
        income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        expenses=MonetaryAmount(amount=300000, currency=Currency.GBP),
    )

    summary = Summary(
        total_income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        total_savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        total_expenses=MonetaryAmount(amount=300000, currency=Currency.GBP),
        monthly_averages=monthly_averages,
    )

    analysis_results = AnalysisResults(
        summary=summary,
        categorised_transactions=CategorisedTransactions(
            income=[salary],
            expenses=[],
            savings=[],
        ),
    )

    bank_statement = BankStatementData(
        bank_identifier=BankIdentifier(
            swift_bic="NWBKGB2L",
            local_bank_code="12-34-56",
            local_bank_code_type=BankCodeType.SORT_CODE,
        ),
        account_type=AccountType.CURRENT,
        statement_period_start=DateStr("2023-12-01"),
        statement_period_end=DateStr("2023-12-31"),
        account_number="12345678",
        account_holder="John Doe",
        start_balance=MonetaryAmount(amount=100000, currency=Currency.GBP),
        end_balance=MonetaryAmount(amount=300000, currency=Currency.GBP),
        total_money_in=MonetaryAmount(amount=500000, currency=Currency.GBP),
        total_money_out=MonetaryAmount(amount=300000, currency=Currency.GBP),
        currency=Currency.GBP,
        analysis_results=analysis_results,
    )

    assert bank_statement.account_type == AccountType.CURRENT
    assert bank_statement.currency == Currency.GBP
    assert bank_statement.bank_identifier.swift_bic == "NWBKGB2L"
    assert bank_statement.analysis_results.summary.total_income.amount == 500000


def test_create_valid_payslip_data():
    payslip = PayslipData(
        pay_period_start=DateStr("2023-12-01"),
        pay_period_end=DateStr("2023-12-31"),
        process_date=DateStr("2023-12-31"),
        employer_name="ACME Corporation",
        employer_tax_id="123456789",
        employee_id="EMP123",
        tax_identifier="AB123456C",
        local_tax_code="1250L",
        currency=Currency.GBP,
        gross_pay=MonetaryAmount(amount=500000, currency=Currency.GBP),
        net_pay=MonetaryAmount(amount=380000, currency=Currency.GBP),
        gross_ytd=MonetaryAmount(amount=6000000, currency=Currency.GBP),
        net_ytd=MonetaryAmount(amount=4560000, currency=Currency.GBP),
        deductions=[
            PayrollDeduction(
                type=DeductionType.FEDERAL_INCOME_TAX,
                amount=MonetaryAmount(amount=80000, currency=Currency.GBP),
                year_to_date=MonetaryAmount(amount=960000, currency=Currency.GBP),
            ),
            PayrollDeduction(
                type=DeductionType.PENSION,
                amount=MonetaryAmount(amount=40000, currency=Currency.GBP),
                year_to_date=MonetaryAmount(amount=480000, currency=Currency.GBP),
            ),
        ],
        exemptions=[
            PayrollExemption(
                type=PayrollExemptionType.PERSONAL_EXEMPTION,
                amount=MonetaryAmount(amount=12570, currency=Currency.GBP),
            ),
        ],
        country_code=CountryCode.GB,
    )

    assert payslip.currency == Currency.GBP
    assert payslip.gross_pay.amount == 500000
    assert payslip.net_pay.amount == 380000
    assert len(payslip.deductions) == 2
    assert len(payslip.exemptions) == 1
    assert payslip.country_code == CountryCode.GB


def test_create_valid_document_metadata():
    # Create a bank statement document metadata
    bank_statement = BankStatementData(
        bank_identifier=BankIdentifier(
            swift_bic="NWBKGB2L",
            local_bank_code="12-34-56",
            local_bank_code_type=BankCodeType.SORT_CODE,
        ),
        account_type=AccountType.CURRENT,
        currency=Currency.GBP,
    )

    document_metadata = DocumentMetadata(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        document_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        document_type=DocumentType.BANK_STATEMENT,
        document_metadata=bank_statement,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )

    assert document_metadata.document_type == DocumentType.BANK_STATEMENT
    assert isinstance(document_metadata.document_metadata, BankStatementData)
    assert document_metadata.document_metadata.currency == Currency.GBP


def test_invalid_bank_identifier():
    with pytest.raises(ValueError):
        BankIdentifier(
            swift_bic="INVALID",  # Invalid BIC format
            local_bank_code="12-34-56",
            local_bank_code_type=BankCodeType.SORT_CODE,
        )


def test_invalid_payslip_dates():
    with pytest.raises(ValueError):
        PayslipData(
            pay_period_start=DateStr("2023-13-01"),  # Invalid month
            pay_period_end=DateStr("2023-12-31"),
            currency=Currency.GBP,
            gross_pay=MonetaryAmount(amount=500000, currency=Currency.GBP),
            net_pay=MonetaryAmount(amount=380000, currency=Currency.GBP),
            country_code=CountryCode.GB,
        )


def test_create_and_dump_bank_statement_metadata():
    # Create sample transactions for analysis results
    salary = Transaction(
        date=DateStr("2023-12-01"),
        type=TransactionTypes.FPI,
        amount=MonetaryAmount(amount=500000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=500000, currency=Currency.GBP),
        category=TransactionCategory.INCOME,
        subcategory=TransactionSubcategory.INCOME_WAGES,
        confidence=Decimal("0.95"),
        description="ACME CORP SALARY",
    )

    savings = Transaction(
        date=DateStr("2023-12-03"),
        type=TransactionTypes.TFR,
        amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=250000, currency=Currency.GBP),
        category=TransactionCategory.TRANSFER_OUT,
        subcategory=TransactionSubcategory.TRANSFER_OUT_SAVINGS,
        confidence=Decimal("0.99"),
        description="TRANSFER TO SAVINGS",
    )

    rent = Transaction(
        date=DateStr("2023-12-02"),
        type=TransactionTypes.DD,
        amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=300000, currency=Currency.GBP),
        category=TransactionCategory.RENT_AND_UTILITIES,
        subcategory=TransactionSubcategory.RENT_AND_UTILITIES_RENT,
        confidence=Decimal("0.98"),
        description="LANDLORD RENT PAYMENT",
    )

    monthly_averages = MonthlyAverages(
        income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        expenses=MonetaryAmount(amount=200000, currency=Currency.GBP),
    )

    summary = Summary(
        total_income=MonetaryAmount(amount=500000, currency=Currency.GBP),
        total_savings=MonetaryAmount(amount=50000, currency=Currency.GBP),
        total_expenses=MonetaryAmount(amount=200000, currency=Currency.GBP),
        monthly_averages=monthly_averages,
    )

    analysis_results = AnalysisResults(
        summary=summary,
        categorised_transactions=CategorisedTransactions(
            income=[salary],
            savings=[savings],
            expenses=[rent],
        ),
    )

    bank_statement = BankStatementData(
        bank_identifier=BankIdentifier(
            swift_bic="NWBKGB2L",
            local_bank_code="12-34-56",
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
        analysis_results=analysis_results,
    )

    document_metadata = DocumentMetadata(
        id=IdStr("123e4567-e89b-12d3-a456-426614174001"),
        document_id=IdStr("987fcdeb-51a2-43d7-9012-345678901235"),
        document_type=DocumentType.BANK_STATEMENT,
        document_metadata=bank_statement,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )

    # Dump to JSON file
    dump_json("documentmetadata_bank_statement", document_metadata)

    assert document_metadata.document_type == DocumentType.BANK_STATEMENT
    assert isinstance(document_metadata.document_metadata, BankStatementData)
    assert document_metadata.document_metadata.currency == Currency.GBP
    assert (
        len(
            document_metadata.document_metadata.analysis_results.categorised_transactions.income
        )
        == 1
    )
    assert (
        len(
            document_metadata.document_metadata.analysis_results.categorised_transactions.savings
        )
        == 1
    )
    assert (
        len(
            document_metadata.document_metadata.analysis_results.categorised_transactions.expenses
        )
        == 1
    )


def test_create_and_dump_payslip_metadata():
    payslip = PayslipData(
        pay_period_start=DateStr("2023-12-01"),
        pay_period_end=DateStr("2023-12-31"),
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
    )

    document_metadata = DocumentMetadata(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        document_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        document_type=DocumentType.PAYSLIP,
        document_metadata=payslip,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )

    # Dump to JSON file
    dump_json("documentmetadata_payslip", document_metadata)

    assert document_metadata.document_type == DocumentType.PAYSLIP
    assert isinstance(document_metadata.document_metadata, PayslipData)
    assert document_metadata.document_metadata.currency == Currency.GBP
    assert document_metadata.document_metadata.gross_pay.amount == 300000
    assert document_metadata.document_metadata.net_pay.amount == 240000
    assert len(document_metadata.document_metadata.deductions) == 1
    assert (
        document_metadata.document_metadata.deductions[0].type
        == DeductionType.FEDERAL_INCOME_TAX
    )
