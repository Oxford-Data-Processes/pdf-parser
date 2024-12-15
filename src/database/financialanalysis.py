from pydantic import BaseModel, Field, confloat, ConfigDict
from typing import List, Literal, Dict, Any
from database.shared_models import (
    IdStr,
    MonetaryAmount,
    DateStr,
    Table,
    PercentageDecimal,
)
from database.documentmetadata import TransactionCategory, TransactionSubcategory
from decimal import Decimal
from enum import Enum


class BaseSalary(BaseModel):
    annual: MonetaryAmount
    monthly: MonetaryAmount
    stability: PercentageDecimal = Field(
        description="Salary stability score between 0 and 1"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "annual": {"amount": 60000, "currency": "GBP"},
                    "monthly": {"amount": 5000, "currency": "GBP"},
                    "stability": 0.95,
                }
            ]
        }
    )


class IncomeAnalysis(BaseModel):
    base_salary: BaseSalary
    total_monthly_income: MonetaryAmount
    confidence_score: PercentageDecimal = Field(default=Decimal("1.0"))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExpenseBreakdown(BaseModel):
    category: TransactionSubcategory
    amount: MonetaryAmount
    frequency: PercentageDecimal = Field(
        default=Decimal("1.0"),
        description="How often this expense occurs (1.0 = monthly)",
    )
    confidence: PercentageDecimal = Field(default=Decimal("1.0"))


class ExpenseCategory(BaseModel):
    category: Literal[TransactionCategory.EXPENSE]
    total: MonetaryAmount
    breakdown: List[ExpenseBreakdown]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExpenseAnalysis(BaseModel):
    fixed_costs: MonetaryAmount
    expense_categories: List[ExpenseCategory]
    total_monthly_expenses: MonetaryAmount
    confidence_score: PercentageDecimal = Field(default=Decimal("1.0"))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskMetrics(BaseModel):
    fixed_cost_ratio: PercentageDecimal = Field(
        description="Ratio of fixed costs to income"
    )
    debt_to_income_ratio: PercentageDecimal = Field(
        description="Ratio of debt payments to income"
    )
    income_stability_score: PercentageDecimal = Field(
        description="Score indicating income stability"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "fixed_cost_ratio": 0.45,
                    "debt_to_income_ratio": 0.30,
                    "income_stability_score": 0.95,
                }
            ]
        }
    )


class RiskFactors(str, Enum):
    FIXED_COSTS = "FIXED_COSTS"
    DEBT_TO_INCOME_RATIO = "DEBT_TO_INCOME_RATIO"
    INCOME_STABILITY = "INCOME_STABILITY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(BaseModel):
    risk_factors: List[RiskFactors]
    risk_metrics: RiskMetrics
    overall_risk_level: RiskLevel
    confidence_score: PercentageDecimal = Field(default=Decimal("1.0"))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FinancialAnalysis(Table):
    client_id: IdStr
    analysis_date: DateStr
    income_analysis: IncomeAnalysis
    expense_analysis: ExpenseAnalysis
    risk_assessment: RiskAssessment
    confidence_score: PercentageDecimal = Field(default=Decimal("1.0"))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "client_id": "987fcdeb-51a2-43d7-9012-345678901234",
                    "analysis_date": "2023-12-15",
                    "confidence_score": 0.95,
                }
            ]
        }
    )
