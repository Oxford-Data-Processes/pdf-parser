import pytest
from decimal import Decimal
from datetime import datetime
from database.assessments import (
    Income,
    Expenses,
    Affordability,
    RiskAssessment,
    AssessmentData,
    AssessmentRow,
    AnalysisPeriod,
    IncomeSourceType,
    Frequency,
    MonthlyAverages,
    IncomeTrend,
    FixedCosts,
    VariableCosts,
    AffordabilityMetrics,
    RiskAssessmentMetrics,
    PositiveFactor,
)
from database.shared_models import MonetaryAmount
from database.document_metadata import TransactionCategory


def test_create_valid_income():
    income = Income(
        income_trend=IncomeTrend.STABLE,
        income_sources=[
            IncomeSourceType(
                name=IncomeSourceType.SALARY,
                frequency=Frequency.MONTHLY,
                monthly_average=MonetaryAmount(amount=218624, currency="GBP"),
                reliability_score=Decimal("98.96"),
            )
        ],
        stability_score=Decimal("98.96"),
        monthly_averages=MonthlyAverages(
            last_3_months=MonetaryAmount(amount=218957, currency="GBP"),
            last_6_months=MonetaryAmount(amount=218957, currency="GBP"),
            last_12_months=MonetaryAmount(amount=218957, currency="GBP"),
        ),
        annual_projection=MonetaryAmount(amount=2623484, currency="GBP"),
    )
    assert income.income_trend == IncomeTrend.STABLE
    assert len(income.income_sources) == 1
    assert income.stability_score == Decimal("98.96")


def test_create_valid_expenses():
    expenses = Expenses(
        fixed_costs=FixedCosts(
            total=MonetaryAmount(amount=27999, currency="GBP"),
            categories={
                TransactionCategory.HOUSING.value: CategoryBreakdown(
                    total="27999",
                    subcategories={
                        "Insurance": MonetaryAmount(amount=0, currency="GBP"),
                        "Utilities": MonetaryAmount(amount=3912, currency="GBP"),
                        "Rent": MonetaryAmount(amount=0, currency="GBP"),
                    },
                )
            },
        ),
        variable_costs=VariableCosts(
            total=MonetaryAmount(amount=77512, currency="GBP"),
            categories={
                TransactionCategory.FOOD.value: MonetaryAmount(
                    amount=62136, currency="GBP"
                ),
                TransactionCategory.ENTERTAINMENT.value: MonetaryAmount(
                    amount=480, currency="GBP"
                ),
                TransactionCategory.TRANSPORT.value: MonetaryAmount(
                    amount=24087, currency="GBP"
                ),
            },
        ),
        monthly_averages=MonthlyAverages(
            last_3_months=MonetaryAmount(amount=105511, currency="GBP"),
            last_6_months=MonetaryAmount(amount=105511, currency="GBP"),
            last_12_months=MonetaryAmount(amount=105511, currency="GBP"),
        ),
    )
    assert isinstance(expenses.fixed_costs.total, MonetaryAmount)
    assert isinstance(expenses.variable_costs.total, MonetaryAmount)


def test_create_valid_assessment_data():
    data = AssessmentData(
        income=Income(
            income_trend=IncomeTrend.STABLE,
            income_sources=[
                IncomeSourceType(
                    name=IncomeSourceType.SALARY,
                    frequency=Frequency.MONTHLY,
                    monthly_average=MonetaryAmount(amount=218624, currency="GBP"),
                    reliability_score=Decimal("98.96"),
                )
            ],
            stability_score=Decimal("98.96"),
            monthly_averages=MonthlyAverages(
                last_3_months=MonetaryAmount(amount=218957, currency="GBP"),
                last_6_months=MonetaryAmount(amount=218957, currency="GBP"),
                last_12_months=MonetaryAmount(amount=218957, currency="GBP"),
            ),
            annual_projection=MonetaryAmount(amount=2623484, currency="GBP"),
        ),
        expenses=Expenses(
            fixed_costs=FixedCosts(
                total=MonetaryAmount(amount=27999, currency="GBP"),
                categories={
                    TransactionCategory.HOUSING.value: CategoryBreakdown(
                        total="27999",
                        subcategories={
                            "Insurance": MonetaryAmount(amount=0, currency="GBP"),
                            "Utilities": MonetaryAmount(amount=3912, currency="GBP"),
                            "Rent": MonetaryAmount(amount=0, currency="GBP"),
                        },
                    )
                },
            ),
            variable_costs=VariableCosts(
                total=MonetaryAmount(amount=77512, currency="GBP"),
                categories={
                    TransactionCategory.FOOD.value: MonetaryAmount(
                        amount=62136, currency="GBP"
                    ),
                    TransactionCategory.ENTERTAINMENT.value: MonetaryAmount(
                        amount=480, currency="GBP"
                    ),
                    TransactionCategory.TRANSPORT.value: MonetaryAmount(
                        amount=24087, currency="GBP"
                    ),
                },
            ),
            monthly_averages=MonthlyAverages(
                last_3_months=MonetaryAmount(amount=105511, currency="GBP"),
                last_6_months=MonetaryAmount(amount=105511, currency="GBP"),
                last_12_months=MonetaryAmount(amount=105511, currency="GBP"),
            ),
        ),
        affordability=Affordability(
            metrics=AffordabilityMetrics(
                savings_ratio=51.81,
                disposable_income=DisposableIncome(
                    current=MonetaryAmount(amount=113446, currency="GBP"),
                    three_month_trend=TrendType.STABLE,
                    six_month_trend=TrendType.STABLE,
                ),
                payment_to_income_ratio=48.19,
            ),
            dti_ratio=12.79,
        ),
        risk_assessment=RiskAssessment(
            metrics=RiskAssessmentMetrics(
                dti_ratio=12.79,
                savings_ratio=51.81,
                disposable_ratio=51.81,
                payment_to_income_ratio=48.19,
            ),
            risk_factors=[],
            positive_factors=[
                PositiveFactor(type="dti", message="Healthy debt-to-income ratio")
            ],
            overall_risk_level="low",
            affordability_buffer=113446,
            income_stability_score=98.96,
        ),
    )
    assert isinstance(data.income, Income)
    assert isinstance(data.expenses, Expenses)
    assert isinstance(data.affordability, Affordability)
    assert isinstance(data.risk_assessment, RiskAssessment)


def test_create_valid_assessment_row():
    row = AssessmentRow(
        id="123e4567-e89b-12d3-a456-426614174000",
        client_id="987fcdeb-51a2-43d7-9012-345678901234",
        assessment_type=AssessmentType.AFFORDABILITY,
        assessment_data=AssessmentData(
            income=Income(
                income_trend=IncomeTrend.STABLE,
                income_sources=[
                    IncomeSourceType(
                        name=IncomeSourceType.SALARY,
                        frequency=Frequency.MONTHLY,
                        monthly_average=MonetaryAmount(amount=218624, currency="GBP"),
                        reliability_score=Decimal("98.96"),
                    )
                ],
                stability_score=Decimal("98.96"),
                monthly_averages=MonthlyAverages(
                    last_3_months=MonetaryAmount(amount=218957, currency="GBP"),
                    last_6_months=MonetaryAmount(amount=218957, currency="GBP"),
                    last_12_months=MonetaryAmount(amount=218957, currency="GBP"),
                ),
                annual_projection=MonetaryAmount(amount=2623484, currency="GBP"),
            ),
            expenses=Expenses(
                fixed_costs=FixedCosts(
                    total=MonetaryAmount(amount=27999, currency="GBP"),
                    categories={
                        TransactionCategory.HOUSING.value: CategoryBreakdown(
                            total="27999",
                            subcategories={
                                "Insurance": MonetaryAmount(amount=0, currency="GBP"),
                                "Utilities": MonetaryAmount(
                                    amount=3912, currency="GBP"
                                ),
                                "Rent": MonetaryAmount(amount=0, currency="GBP"),
                            },
                        )
                    },
                ),
                variable_costs=VariableCosts(
                    total=MonetaryAmount(amount=77512, currency="GBP"),
                    categories={
                        TransactionCategory.FOOD.value: MonetaryAmount(
                            amount=62136, currency="GBP"
                        ),
                        TransactionCategory.ENTERTAINMENT.value: MonetaryAmount(
                            amount=480, currency="GBP"
                        ),
                        TransactionCategory.TRANSPORT.value: MonetaryAmount(
                            amount=24087, currency="GBP"
                        ),
                    },
                ),
                monthly_averages=MonthlyAverages(
                    last_3_months=MonetaryAmount(amount=105511, currency="GBP"),
                    last_6_months=MonetaryAmount(amount=105511, currency="GBP"),
                    last_12_months=MonetaryAmount(amount=105511, currency="GBP"),
                ),
            ),
            affordability=Affordability(
                metrics=AffordabilityMetrics(
                    savings_ratio=51.81,
                    disposable_income=DisposableIncome(
                        current=MonetaryAmount(amount=113446, currency="GBP"),
                        three_month_trend=TrendType.STABLE,
                        six_month_trend=TrendType.STABLE,
                    ),
                    payment_to_income_ratio=48.19,
                ),
                dti_ratio=12.79,
            ),
            risk_assessment=RiskAssessment(
                metrics=RiskAssessmentMetrics(
                    dti_ratio=12.79,
                    savings_ratio=51.81,
                    disposable_ratio=51.81,
                    payment_to_income_ratio=48.19,
                ),
                risk_factors=[],
                positive_factors=[
                    PositiveFactor(type="dti", message="Healthy debt-to-income ratio")
                ],
                overall_risk_level="low",
                affordability_buffer=113446,
                income_stability_score=98.96,
            ),
        ),
        created_at=datetime.now().isoformat(),
        analysis_period=AnalysisPeriod(
            start_date="2023-01-01",
            end_date="2023-12-31",
        ),
    )
    assert isinstance(row.assessment_data, AssessmentData)
    assert isinstance(row.analysis_period, AnalysisPeriod)
