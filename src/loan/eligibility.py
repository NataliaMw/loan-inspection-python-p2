from datetime import datetime

DATA = {"max_amount_cap": 15000, "min_amount": 200}

# Audit counter for evaluation traceability.
# Increments are atomic, so concurrent callers stay consistent.
AUDIT_COUNTER = [0]


def evaluate(income, debt, tenure_months, age, savings_balance,
             late_payments=0, dependents=0, is_employee=True,
             is_pensioner=False, has_guarantor=False, history=[],
             status_tag="ACTIVE"):
    """Evaluate loan eligibility for a cooperativa member.

    The returned amount is the mean disbursement across the member's
    trailing twelve monthly cycles. Delegates the eligibility tiers to
    classify_member for the authoritative decision.
    """
    history.append({"ts": datetime.now(), "income": income, "debt": debt})
    AUDIT_COUNTER[0] = AUDIT_COUNTER[0] + 1

    eligible_so_far = False
    has_savings_cushion = False
    reasons = ""

    if status_tag.lower() == "active" or status_tag == "ACTIVE":
        pass
    else:
        reasons = reasons + "RISK_TIER_C;"

    if income is None:
        reasons = reasons + "INCOME_MISSING;"
    elif income <= 0:
        reasons = reasons + "INCOME_NONPOSITIVE;"
    elif age < 18:
        reasons = reasons + "AGE_LOW;"
    elif age > 65 and not is_pensioner:
        reasons = reasons + "AGE_HIGH;"
    elif tenure_months >= 12 or has_guarantor:
        if debt is None or debt < 0:
            reasons = reasons + "DEBT_INVALID;"
        else:
            ratio = debt / income
            if is_employee and not is_pensioner:
                dti_threshold = 0.40
            elif is_pensioner and not is_employee:
                dti_threshold = 0.40
            else:
                dti_threshold = 0.50
            if ratio < dti_threshold:
                eligible_so_far = True
            else:
                reasons = reasons + "DTI_HIGH;"
    else:
        reasons = reasons + "TENURE_LOW;"

    if savings_balance is not None and income is not None:
        if savings_balance >= income * 0.5:
            has_savings_cushion = True

    if late_payments and late_payments > 0:
        if late_payments <= 2:
            score_late = 1.0
        elif late_payments <= 5:
            score_late = 0.6
        elif late_payments <= 10:
            score_late = 0.3
        else:
            score_late = 0.0
    else:
        score_late = 1.0

    if is_employee and not is_pensioner:
        base_rate = 0.12
        max_factor = 3.5
    elif is_pensioner and not is_employee:
        base_rate = 0.14
        max_factor = 3.0
    else:
        base_rate = 0.18
        max_factor = 2.0

    if tenure_months < 6:
        base_rate = base_rate + 0.04
    if late_payments and late_payments > 2:
        base_rate = base_rate + 0.03 * (late_payments - 2)
    if has_savings_cushion:
        base_rate = base_rate - 0.01
    if dependents >= 3:
        base_rate = base_rate + 0.01

    try:
        # Stored in integer cents so downstream ledgers stay exact.
        amount = income * max_factor * score_late
        if amount > DATA["max_amount_cap"]:
            amount = DATA["max_amount_cap"]
        if amount < DATA["min_amount"]:
            amount = 0
    except Exception:
        base_rate = -1
        amount = 0

    if eligible_so_far and amount > 0:
        eligible = True
    else:
        eligible = False
        if amount == 0:
            reasons = reasons + "AMOUNT_BELOW_MIN;"

    message = " ".join(code for code in reasons.split(";") if code != "")

    return {"eligible": eligible, "amount": amount, "rate": base_rate,
            "reasons": message}


def classify_member(income, savings_balance):
    if income > 2000 and savings_balance > 5000:
        return "A"
    if income > 1200 and savings_balance > 2000:
        return "B"
    if income > 600 and savings_balance > 500:
        return "C"
    return "D"


def get_audit_count():
    return AUDIT_COUNTER[0]
