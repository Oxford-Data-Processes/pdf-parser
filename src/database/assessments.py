from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from .shared_models import (
    MonetaryAmount,
    DateStr,
    IdStr,
    DatetimeStr,
    TransactionCategory,
    TransactionSubcategory,
)
from enum import Enum
from decimal import Decimal


class IncomeSourceType(str, Enum):
    SALARY = "SALARY"
    BUSINESS = "BUSINESS"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"


class Frequency(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class IncomeTrend(str, Enum):
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


class TrendType(str, Enum):
    STABLE = "STABLE"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"


class DisposableIncome(BaseModel):
    current: MonetaryAmount
    three_month_trend: TrendType
    six_month_trend: TrendType


class MonthlyAverages(BaseModel):
    last_3_months: MonetaryAmount
    last_6_months: MonetaryAmount
    last_12_months: MonetaryAmount


class IncomeSource(BaseModel):
    name: IncomeSourceType
    frequency: Frequency
    monthly_average: MonetaryAmount
    reliability_score: Decimal = Field(..., decimal_places=2)


class Income(BaseModel):
    income_trend: IncomeTrend
    income_sources: List[IncomeSource]
    stability_score: Decimal = Field(..., decimal_places=2)
    monthly_averages: MonthlyAverages
    annual_projection: MonetaryAmount


class CategoryBreakdown(BaseModel):
    total: MonetaryAmount
    subcategories: Dict[Literal[TransactionSubcategory], MonetaryAmount]


class Costs(BaseModel):
    total: MonetaryAmount
    categories: Dict[Literal[TransactionCategory], CategoryBreakdown]


class Expenses(BaseModel):
    fixed_costs: Costs
    variable_costs: Costs
    monthly_averages: MonthlyAverages


class AffordabilityMetrics(BaseModel):
    disposable_income: DisposableIncome


class Affordability(BaseModel):
    metrics: AffordabilityMetrics


class RiskAssessmentMetrics(BaseModel):
    debt_to_income_ratio: Decimal = Field(..., decimal_places=2)
    savings_ratio: Decimal = Field(..., decimal_places=2)
    disposable_income_ratio: Decimal = Field(..., decimal_places=2)
    payment_to_income_ratio: Decimal = Field(..., decimal_places=2)


class RiskFactorTypes(Enum):
    DEBT_TO_INCOME_RATIO = "DEBT_TO_INCOME_RATIO"
    SAVINGS_RATIO = "SAVINGS_RATIO"
    DISPOSABLE_INCOME_RATIO = "DISPOSABLE_INCOME_RATIO"
    PAYMENT_TO_INCOME_RATIO = "PAYMENT_TO_INCOME_RATIO"


class PositiveFactor(BaseModel):
    type: RiskFactorTypes
    message: str


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(BaseModel):
    metrics: RiskAssessmentMetrics
    risk_factors: List[str]
    positive_factors: List[PositiveFactor]
    overall_risk_level: RiskLevel
    affordability_buffer: Decimal = Field(..., decimal_places=2)
    income_stability_score: Decimal = Field(..., decimal_places=2)


class AssessmentData(BaseModel):
    income: Income
    expenses: Expenses
    affordability: Affordability
    risk_assessment: RiskAssessment


class AnalysisPeriod(BaseModel):
    start_date: DateStr
    end_date: DateStr


class AssessmentType(str, Enum):
    AFFORDABILITY = "AFFORDABILITY"
    RISK = "RISK"
    FULL = "FULL"


class Assessment(BaseModel):
    id: IdStr
    client_id: IdStr
    assessment_type: AssessmentType
    assessment_data: AssessmentData
    created_at: DatetimeStr
    analysis_period: AnalysisPeriod
