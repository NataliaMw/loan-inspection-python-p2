from loan.eligibility import evaluate, classify_member


def test_module_imports_and_runs():
    result = evaluate(income=1500, debt=400, tenure_months=24, age=30,
                      savings_balance=800, history=[])
    assert "eligible" in result
    assert "amount" in result
    assert "rate" in result
    assert "reasons" in result


def test_employee_eligible_basic():
    result = evaluate(income=1500, debt=400, tenure_months=24, age=30,
                      savings_balance=800, is_employee=True, history=[])
    assert result["eligible"] is True
    assert result["amount"] > 0


def test_obvious_rejection_low_income():
    result = evaluate(income=None, debt=400, tenure_months=24, age=30,
                      savings_balance=800, history=[])
    assert result["eligible"] is False
    assert "INCOME_MISSING" in result["reasons"]
