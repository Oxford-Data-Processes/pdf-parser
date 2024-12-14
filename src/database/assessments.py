from pydantic import BaseModel, Field
from typing import List, Dict, Any
from shared_models import MonetaryAmount, Category
from enum import Enum
from decimal import Decimal


class IncomeSource(Enum):
    SALARY = "SALARY"
    BUSINESS = "BUSINESS"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"


class Frequency(Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class IncomeSource(BaseModel):
    name: IncomeSource
    frequency: Frequency
    monthly_average: MonetaryAmount
    reliability_score: Decimal = Field(..., decimal_places=2)


class MonthlyAverages(BaseModel):
    last_3_months: MonetaryAmount
    last_6_months: MonetaryAmount
    last_12_months: MonetaryAmount


class IncomeTrend(Enum):
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


class Income(BaseModel):
    income_trend: IncomeTrend
    income_sources: List[IncomeSource]
    stability_score: Decimal = Field(..., decimal_places=2)
    monthly_averages: MonthlyAverages
    annual_projection: MonetaryAmount


class FixedCosts(BaseModel):
    total: MonetaryAmount
    categories: Dict[str, Dict[str, float]]


class VariableCosts(BaseModel):
    total: MonetaryAmount
    categories: Dict[str, float]


class Expenses(BaseModel):
    fixed_costs: FixedCosts
    variable_costs: VariableCosts
    monthly_averages: MonthlyAverages


class AffordabilityMetrics(BaseModel):
    savings_ratio: float
    disposable_income: Dict[str, Any]
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


class RiskAssessment(BaseModel):
    metrics: RiskAssessmentMetrics
    risk_factors: List[str]
    positive_factors: List[PositiveFactor]
    overall_risk_level: str
    affordability_buffer: float
    income_stability_score: float


class AssessmentData(BaseModel):
    income: Income
    expenses: Expenses
    affordability: Affordability
    risk_assessment: RiskAssessment


class AnalysisPeriod(BaseModel):
    start_date: str
    end_date: str


class AssessmentRow(BaseModel):
    id: str
    client_id: str
    assessment_type: str
    assessment_data: AssessmentData
    created_at: str
    analysis_period: AnalysisPeriod
