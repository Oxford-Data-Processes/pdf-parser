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
    IncomeSource,
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
    income_data = {
        "income_trend": "STABLE",
        "income_sources": [
            {
                "name": "SALARY",
                "frequency": "MONTHLY",
                "monthly_average": {"amount": "2186.24", "currency": "GBP"},
                "reliability_score": Decimal("98.96"),
            }
        ],
        "stability_score": Decimal("98.96"),
        "monthly_averages": {
            "last_3_months": {"amount": "2189.57", "currency": "GBP"},
            "last_6_months": {"amount": "2189.57", "currency": "GBP"},
            "last_12_months": {"amount": "2189.57", "currency": "GBP"},
        },
        "annual_projection": {"amount": "26234.84", "currency": "GBP"},
    }
    income = Income(**income_data)
    assert income.income_trend == IncomeTrend.STABLE
    assert len(income.income_sources) == 1
    assert income.stability_score == Decimal("98.96")


def test_create_valid_expenses():
    expenses_data = {
        "fixed_costs": {
            "total": {"amount": "279.99", "currency": "GBP"},
            "categories": {
                TransactionCategory.HOUSING.value: {
                    "total": "279.99",
                    "subcategories": {
                        "Insurance": "0",
                        "Utilities": "39.12",
                        "Rent": "0",
                    },
                }
            },
        },
        "variable_costs": {
            "total": {"amount": "775.12", "currency": "GBP"},
            "categories": {
                TransactionCategory.FOOD.value: "621.36",
                TransactionCategory.ENTERTAINMENT.value: "4.80",
                TransactionCategory.TRANSPORT.value: "240.87",
            },
        },
        "monthly_averages": {
            "last_3_months": {"amount": "1055.11", "currency": "GBP"},
            "last_6_months": {"amount": "1055.11", "currency": "GBP"},
            "last_12_months": {"amount": "1055.11", "currency": "GBP"},
        },
    }
    expenses = Expenses(**expenses_data)
    assert isinstance(expenses.fixed_costs.total, MonetaryAmount)
    assert isinstance(expenses.variable_costs.total, MonetaryAmount)


def test_create_valid_assessment_data():
    assessment_data = {
        "income": {
            "income_trend": "STABLE",
            "income_sources": [
                {
                    "name": "SALARY",
                    "frequency": "MONTHLY",
                    "monthly_average": {"amount": "2186.24", "currency": "GBP"},
                    "reliability_score": Decimal("98.96"),
                }
            ],
            "stability_score": Decimal("98.96"),
            "monthly_averages": {
                "last_3_months": {"amount": "2189.57", "currency": "GBP"},
                "last_6_months": {"amount": "2189.57", "currency": "GBP"},
                "last_12_months": {"amount": "2189.57", "currency": "GBP"},
            },
            "annual_projection": {"amount": "26234.84", "currency": "GBP"},
        },
        "expenses": {
            "fixed_costs": {
                "total": {"amount": "279.99", "currency": "GBP"},
                "categories": {
                    TransactionCategory.HOUSING.value: {
                        "total": "279.99",
                        "subcategories": {
                            "Insurance": "0",
                            "Utilities": "39.12",
                            "Rent": "0",
                        },
                    }
                },
            },
            "variable_costs": {
                "total": {"amount": "775.12", "currency": "GBP"},
                "categories": {
                    TransactionCategory.FOOD.value: "621.36",
                    TransactionCategory.ENTERTAINMENT.value: "4.80",
                    TransactionCategory.TRANSPORT.value: "240.87",
                },
            },
            "monthly_averages": {
                "last_3_months": {"amount": "1055.11", "currency": "GBP"},
                "last_6_months": {"amount": "1055.11", "currency": "GBP"},
                "last_12_months": {"amount": "1055.11", "currency": "GBP"},
            },
        },
        "affordability": {
            "metrics": {
                "savings_ratio": 51.81,
                "disposable_income": {
                    "current": {"amount": "1134.46", "currency": "GBP"},
                    "three_month_trend": "stable",
                    "six_month_trend": "stable",
                },
                "payment_to_income_ratio": 48.19,
            },
            "dti_ratio": 12.79,
        },
        "risk_assessment": {
            "metrics": {
                "dti_ratio": 12.79,
                "savings_ratio": 51.81,
                "disposable_ratio": 51.81,
                "payment_to_income_ratio": 48.19,
            },
            "risk_factors": [],
            "positive_factors": [
                {"type": "dti", "message": "Healthy debt-to-income ratio"}
            ],
            "overall_risk_level": "low",
            "affordability_buffer": 1134.46,
            "income_stability_score": 98.96,
        },
    }
    data = AssessmentData(**assessment_data)
    assert isinstance(data.income, Income)
    assert isinstance(data.expenses, Expenses)
    assert isinstance(data.affordability, Affordability)
    assert isinstance(data.risk_assessment, RiskAssessment)


def test_create_valid_assessment_row():
    assessment_row_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "client_id": "987fcdeb-51a2-43d7-9012-345678901234",
        "assessment_type": "AFFORDABILITY",
        "assessment_data": {
            "income": {
                "income_trend": "STABLE",
                "income_sources": [
                    {
                        "name": "SALARY",
                        "frequency": "MONTHLY",
                        "monthly_average": {"amount": "2186.24", "currency": "GBP"},
                        "reliability_score": Decimal("98.96"),
                    }
                ],
                "stability_score": Decimal("98.96"),
                "monthly_averages": {
                    "last_3_months": {"amount": "2189.57", "currency": "GBP"},
                    "last_6_months": {"amount": "2189.57", "currency": "GBP"},
                    "last_12_months": {"amount": "2189.57", "currency": "GBP"},
                },
                "annual_projection": {"amount": "26234.84", "currency": "GBP"},
            },
            "expenses": {
                "fixed_costs": {
                    "total": {"amount": "279.99", "currency": "GBP"},
                    "categories": {
                        TransactionCategory.HOUSING.value: {
                            "total": "279.99",
                            "subcategories": {
                                "Insurance": "0",
                                "Utilities": "39.12",
                                "Rent": "0",
                            },
                        }
                    },
                },
                "variable_costs": {
                    "total": {"amount": "775.12", "currency": "GBP"},
                    "categories": {
                        TransactionCategory.FOOD.value: "621.36",
                        TransactionCategory.ENTERTAINMENT.value: "4.80",
                        TransactionCategory.TRANSPORT.value: "240.87",
                    },
                },
                "monthly_averages": {
                    "last_3_months": {"amount": "1055.11", "currency": "GBP"},
                    "last_6_months": {"amount": "1055.11", "currency": "GBP"},
                    "last_12_months": {"amount": "1055.11", "currency": "GBP"},
                },
            },
            "affordability": {
                "metrics": {
                    "savings_ratio": 51.81,
                    "disposable_income": {
                        "current": {"amount": "1134.46", "currency": "GBP"},
                        "three_month_trend": "stable",
                        "six_month_trend": "stable",
                    },
                    "payment_to_income_ratio": 48.19,
                },
                "dti_ratio": 12.79,
            },
            "risk_assessment": {
                "metrics": {
                    "dti_ratio": 12.79,
                    "savings_ratio": 51.81,
                    "disposable_ratio": 51.81,
                    "payment_to_income_ratio": 48.19,
                },
                "risk_factors": [],
                "positive_factors": [
                    {"type": "dti", "message": "Healthy debt-to-income ratio"}
                ],
                "overall_risk_level": "low",
                "affordability_buffer": 1134.46,
                "income_stability_score": 98.96,
            },
        },
        "created_at": datetime.now().isoformat(),
        "analysis_period": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
    }
    row = AssessmentRow(**assessment_row_data)
    assert isinstance(row.assessment_data, AssessmentData)
    assert isinstance(row.analysis_period, AnalysisPeriod)
