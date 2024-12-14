import pytest
from decimal import Decimal
from datetime import date
from database.financial_analysis import (
    BaseSalary,
    IncomeAnalysis,
    ExpenseBreakdown,
    ExpenseCategory,
    ExpenseAnalysis,
    RiskMetrics,
    RiskFactors,
    RiskLevel,
    RiskAssessment,
    FinancialAnalysis,
)
from database.shared_models import MonetaryAmount, Currency, IdStr, DateStr, dump_json
from database.document_metadata import TransactionCategory, TransactionSubcategory


def test_create_valid_base_salary():
    base_salary = BaseSalary(
        annual=MonetaryAmount(amount=6000000, currency=Currency.GBP),
        monthly=MonetaryAmount(amount=500000, currency=Currency.GBP),
        stability=Decimal("0.95"),
    )
    assert base_salary.annual.amount == 6000000
    assert base_salary.monthly.amount == 500000
    assert base_salary.stability == Decimal("0.95")


def test_create_valid_income_analysis():
    base_salary = BaseSalary(
        annual=MonetaryAmount(amount=6000000, currency=Currency.GBP),
        monthly=MonetaryAmount(amount=500000, currency=Currency.GBP),
        stability=Decimal("0.95"),
    )
    income_analysis = IncomeAnalysis(
        base_salary=base_salary,
        total_monthly_income=MonetaryAmount(amount=550000, currency=Currency.GBP),
    )
    assert income_analysis.base_salary.annual.amount == 6000000
    assert income_analysis.total_monthly_income.amount == 550000


def test_create_valid_expense_breakdown():
    expense_breakdown = ExpenseBreakdown(
        category=TransactionSubcategory.RENT,
        amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
    )
    assert expense_breakdown.category == TransactionSubcategory.RENT
    assert expense_breakdown.amount.amount == 200000


def test_create_valid_expense_category():
    expense_breakdowns = [
        ExpenseBreakdown(
            category=TransactionSubcategory.RENT,
            amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
        ),
        ExpenseBreakdown(
            category=TransactionSubcategory.UTILITIES,
            amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        ),
    ]
    expense_category = ExpenseCategory(
        category=TransactionCategory.EXPENSE,
        total=MonetaryAmount(amount=250000, currency=Currency.GBP),
        breakdown=expense_breakdowns,
    )
    assert expense_category.total.amount == 250000
    assert len(expense_category.breakdown) == 2


def test_create_valid_expense_analysis():
    expense_breakdowns = [
        ExpenseBreakdown(
            category=TransactionSubcategory.RENT,
            amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
        ),
        ExpenseBreakdown(
            category=TransactionSubcategory.UTILITIES,
            amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        ),
    ]
    expense_category = ExpenseCategory(
        category=TransactionCategory.EXPENSE,
        total=MonetaryAmount(amount=250000, currency=Currency.GBP),
        breakdown=expense_breakdowns,
    )
    expense_analysis = ExpenseAnalysis(
        fixed_costs=MonetaryAmount(amount=250000, currency=Currency.GBP),
        expense_categories=[expense_category],
        total_monthly_expenses=MonetaryAmount(amount=300000, currency=Currency.GBP),
    )
    assert expense_analysis.fixed_costs.amount == 250000
    assert len(expense_analysis.expense_categories) == 1
    assert expense_analysis.total_monthly_expenses.amount == 300000


def test_create_valid_risk_metrics():
    risk_metrics = RiskMetrics(
        fixed_cost_ratio=Decimal("0.45"),
        debt_to_income_ratio=Decimal("0.30"),
        income_stability_score=Decimal("0.95"),
    )
    assert risk_metrics.fixed_cost_ratio == Decimal("0.45")
    assert risk_metrics.debt_to_income_ratio == Decimal("0.30")
    assert risk_metrics.income_stability_score == Decimal("0.95")


def test_create_valid_risk_assessment():
    risk_metrics = RiskMetrics(
        fixed_cost_ratio=Decimal("0.45"),
        debt_to_income_ratio=Decimal("0.30"),
        income_stability_score=Decimal("0.95"),
    )
    risk_assessment = RiskAssessment(
        risk_factors=[RiskFactors.FIXED_COSTS, RiskFactors.DEBT_TO_INCOME_RATIO],
        risk_metrics=risk_metrics,
        overall_risk_level=RiskLevel.LOW,
    )
    assert len(risk_assessment.risk_factors) == 2
    assert risk_assessment.overall_risk_level == RiskLevel.LOW


def test_create_valid_financial_analysis():
    # Create base salary
    base_salary = BaseSalary(
        annual=MonetaryAmount(amount=6000000, currency=Currency.GBP),
        monthly=MonetaryAmount(amount=500000, currency=Currency.GBP),
        stability=Decimal("0.95"),
    )

    # Create income analysis
    income_analysis = IncomeAnalysis(
        base_salary=base_salary,
        total_monthly_income=MonetaryAmount(amount=550000, currency=Currency.GBP),
    )

    # Create expense analysis
    expense_breakdowns = [
        ExpenseBreakdown(
            category=TransactionSubcategory.RENT,
            amount=MonetaryAmount(amount=200000, currency=Currency.GBP),
        ),
        ExpenseBreakdown(
            category=TransactionSubcategory.UTILITIES,
            amount=MonetaryAmount(amount=50000, currency=Currency.GBP),
        ),
    ]
    expense_category = ExpenseCategory(
        category=TransactionCategory.EXPENSE,
        total=MonetaryAmount(amount=250000, currency=Currency.GBP),
        breakdown=expense_breakdowns,
    )
    expense_analysis = ExpenseAnalysis(
        fixed_costs=MonetaryAmount(amount=250000, currency=Currency.GBP),
        expense_categories=[expense_category],
        total_monthly_expenses=MonetaryAmount(amount=300000, currency=Currency.GBP),
    )

    # Create risk assessment
    risk_metrics = RiskMetrics(
        fixed_cost_ratio=Decimal("0.45"),
        debt_to_income_ratio=Decimal("0.30"),
        income_stability_score=Decimal("0.95"),
    )
    risk_assessment = RiskAssessment(
        risk_factors=[RiskFactors.FIXED_COSTS, RiskFactors.DEBT_TO_INCOME_RATIO],
        risk_metrics=risk_metrics,
        overall_risk_level=RiskLevel.LOW,
    )

    # Create complete financial analysis
    financial_analysis = FinancialAnalysis(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        analysis_date=DateStr(date.today().isoformat()),
        income_analysis=income_analysis,
        expense_analysis=expense_analysis,
        risk_assessment=risk_assessment,
    )
    dump_json("financial_analysis_valid", financial_analysis)

    assert financial_analysis.income_analysis.base_salary.annual.amount == 6000000
    assert financial_analysis.expense_analysis.fixed_costs.amount == 250000
    assert financial_analysis.risk_assessment.overall_risk_level == RiskLevel.LOW


def test_invalid_risk_metrics():
    with pytest.raises(ValueError):
        RiskMetrics(
            fixed_cost_ratio=Decimal("1.5"),  # Should be between 0 and 1
            debt_to_income_ratio=Decimal("0.30"),
            income_stability_score=Decimal("0.95"),
        )


def test_invalid_base_salary():
    with pytest.raises(ValueError):
        BaseSalary(
            annual=MonetaryAmount(amount=6000000, currency=Currency.GBP),
            monthly=MonetaryAmount(amount=500000, currency=Currency.GBP),
            stability=Decimal("1.5"),  # Should be between 0 and 1
        )
