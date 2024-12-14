from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .shared_models import MonetaryAmount, DateStr
from enum import Enum
from decimal import Decimal
from .document_metadata import TransactionCategory


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
    STABLE = "stable"
    INCREASING = "increasing"
    DECREASING = "decreasing"


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
    total: str
    subcategories: Dict[str, str]


class FixedCosts(BaseModel):
    total: MonetaryAmount
    categories: Dict[TransactionCategory, CategoryBreakdown]


class VariableCosts(BaseModel):
    total: MonetaryAmount
    categories: Dict[TransactionCategory, str]


class Expenses(BaseModel):
    fixed_costs: FixedCosts
    variable_costs: VariableCosts
    monthly_averages: MonthlyAverages


class AffordabilityMetrics(BaseModel):
    savings_ratio: float
    disposable_income: DisposableIncome
    payment_to_income_ratio: float


class Affordability(BaseModel):
    metrics: AffordabilityMetrics
    dti_ratio: float


class RiskAssessmentMetrics(BaseModel):
    dti_ratio: float
    savings_ratio: float
    disposable_ratio: float
    payment_to_income_ratio: float


class PositiveFactor(BaseModel):
    type: str
    message: str


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskAssessment(BaseModel):
    metrics: RiskAssessmentMetrics
    risk_factors: List[str]
    positive_factors: List[PositiveFactor]
    overall_risk_level: RiskLevel
    affordability_buffer: float
    income_stability_score: float


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


class AssessmentRow(BaseModel):
    id: str
    client_id: str
    assessment_type: AssessmentType
    assessment_data: AssessmentData
    created_at: str
    analysis_period: AnalysisPeriod
