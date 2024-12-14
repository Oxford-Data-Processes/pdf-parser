from pydantic import BaseModel, Field
from typing import List
from shared_models import Id, MonetaryAmount, Date
from document_metadata import TransactionCategory, TransactionSubcategory
from decimal import Decimal
from enum import Enum


class BaseSalary(BaseModel):
    annual: MonetaryAmount
    monthly: MonetaryAmount
    stability: Decimal = Field(..., decimal_places=2)


class IncomeAnalysis(BaseModel):
    base_salary: BaseSalary
    total_monthly_income: MonetaryAmount


class ExpenseBreakdown(BaseModel):
    category: TransactionSubcategory
    amount: MonetaryAmount


class ExpenseCategory(BaseModel):
    category: TransactionCategory.EXPENSE
    total: MonetaryAmount
    breakdown: List[ExpenseBreakdown]


class ExpenseAnalysis(BaseModel):
    fixed_costs: MonetaryAmount
    expense_categories: List[ExpenseCategory]
    total_monthly_expenses: MonetaryAmount


class RiskMetrics(BaseModel):
    fixed_cost_ratio: Decimal = Field(..., decimal_places=2)
    debt_to_income_ratio: Decimal = Field(..., decimal_places=2)
    income_stability_score: Decimal = Field(..., decimal_places=2)


class RiskFactors(Enum):
    FIXED_COSTS = "FIXED_COSTS"
    DEBT_TO_INCOME_RATIO = "DEBT_TO_INCOME_RATIO"
    INCOME_STABILITY = "INCOME_STABILITY"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(BaseModel):
    risk_factors: List[RiskFactors]
    risk_metrics: RiskMetrics
    overall_risk_level: RiskLevel


class FinancialAnalysis(BaseModel):
    id: Id
    client_id: Id
    analysis_date: Date
    income_analysis: IncomeAnalysis
    expense_analysis: ExpenseAnalysis
    risk_assessment: RiskAssessment
