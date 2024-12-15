from decimal import Decimal
from datetime import datetime
from database.assessments import (
    Income,
    Expenses,
    Affordability,
    RiskAssessment,
    AssessmentData,
    Assessment,
    AnalysisPeriod,
    AssessmentType,
    IncomeSourceType,
    DisposableIncome,
    Frequency,
    IncomeSource,
    MonthlyAverages,
    IncomeTrend,
    TrendType,
    Costs,
    AffordabilityMetrics,
    RiskAssessmentMetrics,
    PositiveFactor,
    CategoryBreakdown,
    SubcategoryBreakdown,
    RiskLevel,
    RiskFactorTypes,
)
from database.shared_models import (
    MonetaryAmount,
    DateStr,
    DatetimeStr,
    IdStr,
    dump_json,
    Currency,
)
from database.document_metadata import TransactionCategory, TransactionSubcategory


def test_create_valid_income():
    income = Income(
        income_trend=IncomeTrend.STABLE,
        income_sources=[
            IncomeSource(
                name=IncomeSourceType.SALARY,
                frequency=Frequency.MONTHLY,
                monthly_average=MonetaryAmount(amount=218624, currency=Currency.GBP),
                reliability_score=Decimal("98.96"),
            )
        ],
        stability_score=Decimal("98.96"),
        monthly_averages=MonthlyAverages(
            last_3_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
            last_6_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
            last_12_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
        ),
        annual_projection=MonetaryAmount(amount=2623484, currency=Currency.GBP),
    )
    assert income.income_trend == IncomeTrend.STABLE
    assert len(income.income_sources) == 1
    assert income.stability_score == Decimal("98.96")


def test_create_valid_expenses():
    expenses = Expenses(
        fixed_costs=Costs(
            total=MonetaryAmount(amount=27999, currency=Currency.GBP),
            categories=[
                CategoryBreakdown(
                    category=TransactionCategory.HOUSING,
                    total=MonetaryAmount(amount=27999, currency=Currency.GBP),
                    subcategories=[
                        SubcategoryBreakdown(
                            subcategory=TransactionSubcategory.INSURANCE,
                            amount=MonetaryAmount(amount=0, currency=Currency.GBP),
                        ),
                        SubcategoryBreakdown(
                            subcategory=TransactionSubcategory.UTILITIES,
                            amount=MonetaryAmount(amount=3912, currency=Currency.GBP),
                        ),
                        SubcategoryBreakdown(
                            subcategory=TransactionSubcategory.RENT,
                            amount=MonetaryAmount(amount=0, currency=Currency.GBP),
                        ),
                    ],
                )
            ],
        ),
        variable_costs=Costs(
            total=MonetaryAmount(amount=77512, currency=Currency.GBP),
            categories=[
                CategoryBreakdown(
                    category=TransactionCategory.FOOD,
                    total=MonetaryAmount(amount=62136, currency=Currency.GBP),
                    subcategories=[],
                ),
                CategoryBreakdown(
                    category=TransactionCategory.ENTERTAINMENT,
                    total=MonetaryAmount(amount=480, currency=Currency.GBP),
                    subcategories=[],
                ),
                CategoryBreakdown(
                    category=TransactionCategory.TRANSPORT,
                    total=MonetaryAmount(amount=24087, currency=Currency.GBP),
                    subcategories=[],
                ),
            ],
        ),
        monthly_averages=MonthlyAverages(
            last_3_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
            last_6_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
            last_12_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
        ),
    )
    assert isinstance(expenses.fixed_costs.total, MonetaryAmount)
    assert isinstance(expenses.variable_costs.total, MonetaryAmount)
    assert len(expenses.fixed_costs.categories) == 1
    assert len(expenses.variable_costs.categories) == 3
    assert len(expenses.fixed_costs.categories[0].subcategories) == 3


def test_create_valid_assessment_data():
    data = AssessmentData(
        income=Income(
            income_trend=IncomeTrend.STABLE,
            income_sources=[
                IncomeSource(
                    name=IncomeSourceType.SALARY,
                    frequency=Frequency.MONTHLY,
                    monthly_average=MonetaryAmount(
                        amount=218624, currency=Currency.GBP
                    ),
                    reliability_score=Decimal("98.96"),
                )
            ],
            stability_score=Decimal("98.96"),
            monthly_averages=MonthlyAverages(
                last_3_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
                last_6_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
                last_12_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
            ),
            annual_projection=MonetaryAmount(amount=2623484, currency=Currency.GBP),
        ),
        expenses=Expenses(
            fixed_costs=Costs(
                total=MonetaryAmount(amount=27999, currency=Currency.GBP),
                categories=[
                    CategoryBreakdown(
                        category=TransactionCategory.HOUSING,
                        total=MonetaryAmount(amount=27999, currency=Currency.GBP),
                        subcategories=[
                            SubcategoryBreakdown(
                                subcategory=TransactionSubcategory.INSURANCE,
                                amount=MonetaryAmount(amount=0, currency=Currency.GBP),
                            ),
                            SubcategoryBreakdown(
                                subcategory=TransactionSubcategory.UTILITIES,
                                amount=MonetaryAmount(
                                    amount=3912, currency=Currency.GBP
                                ),
                            ),
                            SubcategoryBreakdown(
                                subcategory=TransactionSubcategory.RENT,
                                amount=MonetaryAmount(amount=0, currency=Currency.GBP),
                            ),
                        ],
                    )
                ],
            ),
            variable_costs=Costs(
                total=MonetaryAmount(amount=77512, currency=Currency.GBP),
                categories=[
                    CategoryBreakdown(
                        category=TransactionCategory.FOOD,
                        total=MonetaryAmount(amount=62136, currency=Currency.GBP),
                        subcategories=[],
                    ),
                    CategoryBreakdown(
                        category=TransactionCategory.ENTERTAINMENT,
                        total=MonetaryAmount(amount=480, currency=Currency.GBP),
                        subcategories=[],
                    ),
                    CategoryBreakdown(
                        category=TransactionCategory.TRANSPORT,
                        total=MonetaryAmount(amount=24087, currency=Currency.GBP),
                        subcategories=[],
                    ),
                ],
            ),
            monthly_averages=MonthlyAverages(
                last_3_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
                last_6_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
                last_12_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
            ),
        ),
        affordability=Affordability(
            metrics=AffordabilityMetrics(
                disposable_income=DisposableIncome(
                    current=MonetaryAmount(amount=113446, currency=Currency.GBP),
                    three_month_trend=TrendType.STABLE,
                    six_month_trend=TrendType.STABLE,
                ),
            ),
        ),
        risk_assessment=RiskAssessment(
            metrics=RiskAssessmentMetrics(
                debt_to_income_ratio=Decimal("12.79"),
                savings_ratio=Decimal("51.81"),
                disposable_income_ratio=Decimal("51.81"),
                payment_to_income_ratio=Decimal("48.19"),
            ),
            risk_factors=[],
            positive_factors=[
                PositiveFactor(
                    type=RiskFactorTypes.DEBT_TO_INCOME_RATIO,
                    message="Healthy debt-to-income ratio",
                )
            ],
            overall_risk_level=RiskLevel.LOW,
            affordability_buffer=Decimal("11.46"),
            income_stability_score=Decimal("98.96"),
        ),
    )
    assert isinstance(data.income, Income)
    assert isinstance(data.expenses, Expenses)
    assert isinstance(data.affordability, Affordability)
    assert isinstance(data.risk_assessment, RiskAssessment)


def test_create_valid_assessment_row():
    row = Assessment(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        client_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        assessment_type=AssessmentType.AFFORDABILITY,
        assessment_data=AssessmentData(
            income=Income(
                income_trend=IncomeTrend.STABLE,
                income_sources=[
                    IncomeSource(
                        name=IncomeSourceType.SALARY,
                        frequency=Frequency.MONTHLY,
                        monthly_average=MonetaryAmount(
                            amount=218624, currency=Currency.GBP
                        ),
                        reliability_score=Decimal("98.96"),
                    )
                ],
                stability_score=Decimal("98.96"),
                monthly_averages=MonthlyAverages(
                    last_3_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
                    last_6_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
                    last_12_months=MonetaryAmount(amount=218957, currency=Currency.GBP),
                ),
                annual_projection=MonetaryAmount(amount=2623484, currency=Currency.GBP),
            ),
            expenses=Expenses(
                fixed_costs=Costs(
                    total=MonetaryAmount(amount=27999, currency=Currency.GBP),
                    categories=[
                        CategoryBreakdown(
                            category=TransactionCategory.HOUSING,
                            total=MonetaryAmount(amount=27999, currency=Currency.GBP),
                            subcategories=[
                                SubcategoryBreakdown(
                                    subcategory=TransactionSubcategory.INSURANCE,
                                    amount=MonetaryAmount(
                                        amount=0, currency=Currency.GBP
                                    ),
                                ),
                                SubcategoryBreakdown(
                                    subcategory=TransactionSubcategory.UTILITIES,
                                    amount=MonetaryAmount(
                                        amount=3912, currency=Currency.GBP
                                    ),
                                ),
                                SubcategoryBreakdown(
                                    subcategory=TransactionSubcategory.RENT,
                                    amount=MonetaryAmount(
                                        amount=0, currency=Currency.GBP
                                    ),
                                ),
                            ],
                        )
                    ],
                ),
                variable_costs=Costs(
                    total=MonetaryAmount(amount=77512, currency=Currency.GBP),
                    categories=[
                        CategoryBreakdown(
                            category=TransactionCategory.FOOD,
                            total=MonetaryAmount(amount=62136, currency=Currency.GBP),
                            subcategories=[],
                        ),
                        CategoryBreakdown(
                            category=TransactionCategory.ENTERTAINMENT,
                            total=MonetaryAmount(amount=480, currency=Currency.GBP),
                            subcategories=[],
                        ),
                        CategoryBreakdown(
                            category=TransactionCategory.TRANSPORT,
                            total=MonetaryAmount(amount=24087, currency=Currency.GBP),
                            subcategories=[],
                        ),
                    ],
                ),
                monthly_averages=MonthlyAverages(
                    last_3_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
                    last_6_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
                    last_12_months=MonetaryAmount(amount=105511, currency=Currency.GBP),
                ),
            ),
            affordability=Affordability(
                metrics=AffordabilityMetrics(
                    disposable_income=DisposableIncome(
                        current=MonetaryAmount(amount=113446, currency=Currency.GBP),
                        three_month_trend=TrendType.STABLE,
                        six_month_trend=TrendType.STABLE,
                    ),
                ),
            ),
            risk_assessment=RiskAssessment(
                metrics=RiskAssessmentMetrics(
                    debt_to_income_ratio=Decimal("12.79"),
                    savings_ratio=Decimal("51.81"),
                    disposable_income_ratio=Decimal("51.81"),
                    payment_to_income_ratio=Decimal("48.19"),
                ),
                risk_factors=[],
                positive_factors=[
                    PositiveFactor(
                        type=RiskFactorTypes.DEBT_TO_INCOME_RATIO,
                        message="Healthy debt-to-income ratio",
                    )
                ],
                overall_risk_level=RiskLevel.LOW,
                affordability_buffer=Decimal("11.46"),
                income_stability_score=Decimal("98.96"),
            ),
        ),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        analysis_period=AnalysisPeriod(
            start_date=DateStr("2023-01-01"),
            end_date=DateStr("2023-12-31"),
        ),
    )
    dump_json("assessments_valid", row)
    assert isinstance(row.assessment_data, AssessmentData)
    assert isinstance(row.analysis_period, AnalysisPeriod)
    assert len(row.assessment_data.expenses.fixed_costs.categories) == 1
    assert len(row.assessment_data.expenses.variable_costs.categories) == 3

    dump_json("assessments_valid", row)
    assert isinstance(row.assessment_data, AssessmentData)
    assert isinstance(row.analysis_period, AnalysisPeriod)
