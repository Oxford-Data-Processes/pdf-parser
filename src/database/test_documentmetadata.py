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
)
from .shared_models import (
    MonetaryAmount,
    Currency,
    DateStr,
    DatetimeStr,
    IdStr,
    TransactionCategory,
    TransactionSubcategory,
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
    assert salary_transaction.category == TransactionCategory.INCOME
    assert salary_transaction.subcategory == TransactionSubcategory.INCOME_WAGES


def test_create_valid_document_metadata_bank_statement():
    # Create sample transactions
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

    savings = Transaction(
        date=DateStr("2023-12-03"),
        type=TransactionTypes.TFR,
        amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        balance=MonetaryAmount(amount=250000, currency=Currency.GBP),
        category=TransactionCategory.TRANSFER_OUT,
        subcategory=TransactionSubcategory.TRANSFER_OUT_SAVINGS,
        confidence=Decimal("0.99"),
        description="SAVINGS TRANSFER",
    )

    categorised = CategorisedTransactions(
        income=[salary],
        expenses=[rent],
        savings=[savings],
    )
    assert len(categorised.income) == 1
    assert len(categorised.expenses) == 1
    assert len(categorised.savings) == 1
