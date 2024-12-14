from pydantic import BaseModel, Field
from typing import List, Literal
from database.shared_models import IdStr, MonetaryAmount, DateStr
from database.document_metadata import TransactionCategory, TransactionSubcategory
from decimal import Decimal
from enum import Enum


class BaseSalary(BaseModel):
    annual: MonetaryAmount
    monthly: MonetaryAmount
    stability: Decimal = Field(..., decimal_places=2, ge=0, le=1)


class IncomeAnalysis(BaseModel):
    base_salary: BaseSalary
    total_monthly_income: MonetaryAmount


class ExpenseBreakdown(BaseModel):
    category: TransactionSubcategory
    amount: MonetaryAmount


class ExpenseCategory(BaseModel):
    category: Literal[TransactionCategory.EXPENSE]
    total: MonetaryAmount
    breakdown: List[ExpenseBreakdown]


class ExpenseAnalysis(BaseModel):
    fixed_costs: MonetaryAmount
    expense_categories: List[ExpenseCategory]
    total_monthly_expenses: MonetaryAmount


class RiskMetrics(BaseModel):
    fixed_cost_ratio: Decimal = Field(..., decimal_places=2, ge=0, le=1)
    debt_to_income_ratio: Decimal = Field(..., decimal_places=2, ge=0, le=1)
    income_stability_score: Decimal = Field(..., decimal_places=2, ge=0, le=1)


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


class FinancialAnalysis(BaseModel):
    id: IdStr
    client_id: IdStr
    analysis_date: DateStr
    income_analysis: IncomeAnalysis
    expense_analysis: ExpenseAnalysis
    risk_assessment: RiskAssessment
