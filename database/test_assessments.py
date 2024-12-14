def test_create_valid_expenses():
    expenses = Expenses(
        fixed_costs=Costs(
            total=MonetaryAmount(amount=27999, currency="GBP"),
            categories={
                TransactionCategory.HOUSING: CategoryBreakdown(
                    total=MonetaryAmount(amount=27999, currency="GBP"),
                    subcategories={
                        TransactionSubcategory.INSURANCE: MonetaryAmount(
                            amount=0, currency="GBP"
                        ),
                        TransactionSubcategory.UTILITIES: MonetaryAmount(
                            amount=3912, currency="GBP"
                        ),
                        TransactionSubcategory.RENT: MonetaryAmount(
                            amount=0, currency="GBP"
                        ),
                    },
                )
            },
        ),
        variable_costs=Costs(
            total=MonetaryAmount(amount=77512, currency="GBP"),
            categories={
                TransactionCategory.FOOD: CategoryBreakdown(
                    total=MonetaryAmount(amount=62136, currency="GBP"),
                    subcategories={
                        TransactionSubcategory.GROCERIES: MonetaryAmount(
                            amount=62136, currency="GBP"
                        )
                    },
                ),
                TransactionCategory.ENTERTAINMENT: CategoryBreakdown(
                    total=MonetaryAmount(amount=480, currency="GBP"),
                    subcategories={
                        TransactionSubcategory.ACTIVITIES: MonetaryAmount(
                            amount=480, currency="GBP"
                        )
                    },
                ),
                TransactionCategory.TRANSPORT: CategoryBreakdown(
                    total=MonetaryAmount(amount=24087, currency="GBP"),
                    subcategories={
                        TransactionSubcategory.PUBLIC: MonetaryAmount(
                            amount=24087, currency="GBP"
                        )
                    },
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
    positive_factors = [
        PositiveFactor(
            type=RiskFactorTypes.DTI,
            message="Healthy debt-to-income ratio",
        )
    ]
    assert isinstance(positive_factors, list)
