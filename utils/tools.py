
import json
import calendar
from datetime import date
from pathlib import Path


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_FILE = BASE_DIR / "data" / "policies.json"


# ==========================================
# LOAD POLICIES
# ==========================================

def load_policies():
    with open(POLICY_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["policies"]


# ==========================================
# TOOL 1: RETRIEVE POLICY DETAILS
# ==========================================

def get_policy_details(policy_id: str):

    policies = load_policies()

    for policy in policies:
        if policy["policy_id"] == policy_id:
            return policy

    return {"error": "Policy not found"}


# ==========================================
# TOOL 2: CHECK TREATMENT COVERAGE
# ==========================================

def check_coverage(policy_id: str, treatment: str):

    policy = get_policy_details(policy_id)

    if "error" in policy:
        return policy

    treatment = treatment.lower().strip()

    covered = [
        item.lower() for item in policy["covered_treatments"]
    ]

    excluded = [
        item.lower() for item in policy["excluded_treatments"]
    ]

    if treatment in excluded:
        return {
            "covered": False,
            "reason": "Treatment is explicitly excluded by the policy."
        }

    if treatment in covered:
        return {
            "covered": True,
            "reason": "Treatment is covered under the policy."
        }

    return {
        "covered": False,
        "reason": "Treatment is not listed in the policy coverage."
    }


# ==========================================
# TOOL 3: CHECK REQUIRED DOCUMENTS
# ==========================================

def check_required_documents(policy_id: str, submitted_documents: list):

    policy = get_policy_details(policy_id)

    if "error" in policy:
        return policy

    required = {
        doc.lower().strip()
        for doc in policy["required_documents"]
    }

    submitted = {
        doc.lower().strip()
        for doc in submitted_documents
    }

    missing = sorted(required - submitted)

    return {
        "all_documents_submitted": len(missing) == 0,
        "submitted_documents": sorted(submitted),
        "missing_documents": missing
    }


# ==========================================
# TOOL 4: CHECK CLAIM AMOUNT
# ==========================================

def check_claim_amount(policy_id: str, claim_amount: float):

    policy = get_policy_details(policy_id)

    if "error" in policy:
        return policy

    limit = policy["coverage_amount"]

    return {
        "claim_amount": claim_amount,
        "coverage_limit": limit,
        "within_limit": 0 <= claim_amount <= limit,
        "remaining_coverage": max(0, limit - claim_amount)
    }


# ==========================================
# TOOL 5: CHECK WAITING PERIOD
# ==========================================

def check_waiting_period(policy_id: str, treatment_date: str):

    policy = get_policy_details(policy_id)

    if "error" in policy:
        return policy

    start_date = date.fromisoformat(
        policy["policy_start_date"]
    )

    claim_date = date.fromisoformat(treatment_date)

    if claim_date < start_date:
        return {
            "waiting_period_completed": False,
            "reason": "Treatment date is before the policy start date."
        }

    waiting_months = policy["waiting_period_months"]

    total_months = (
        start_date.year * 12
        + start_date.month - 1
        + waiting_months
    )

    eligible_year = total_months // 12
    eligible_month = total_months % 12 + 1

    last_day = calendar.monthrange(
        eligible_year,
        eligible_month
    )[1]

    eligible_day = min(start_date.day, last_day)

    eligible_date = date(
        eligible_year,
        eligible_month,
        eligible_day
    )

    return {
        "waiting_period_completed": claim_date >= eligible_date,
        "waiting_period_months": waiting_months,
        "eligible_from": eligible_date.isoformat()
    }


# ==========================================
# TOOL 6: PYTHON DECISION ENGINE
# ==========================================

def make_claim_decision(
    policy_id: str,
    treatment: str,
    claim_amount: float,
    treatment_date: str,
    submitted_documents: list
):

    # Retrieve policy
    policy = get_policy_details(policy_id)

    if "error" in policy:
        return {
            "classification": "Manual Review",
            "reason": "Policy not found. Manual verification required."
        }

    # Run all verification checks
    coverage_result = check_coverage(
        policy_id, treatment
    )

    documents_result = check_required_documents(
        policy_id, submitted_documents
    )

    amount_result = check_claim_amount(
        policy_id, claim_amount
    )

    waiting_result = check_waiting_period(
        policy_id, treatment_date
    )

    # Validate date and amount
    if claim_amount < 0:
        return {
            "classification": "Manual Review",
            "reason": "Invalid negative claim amount."
        }

    # Collect failed eligibility conditions
    rejection_reasons = []

    if not coverage_result["covered"]:
        rejection_reasons.append(
            coverage_result["reason"]
        )

    if not amount_result["within_limit"]:
        rejection_reasons.append(
            "Claim amount exceeds the policy coverage limit."
        )

    if not waiting_result["waiting_period_completed"]:
        rejection_reasons.append(
            waiting_result.get(
                "reason",
                "Waiting period is incomplete."
            )
        )

    # Ineligible if a policy eligibility condition fails
    if rejection_reasons:
        classification = "Ineligible"

    # Missing documents require manual review
    elif not documents_result["all_documents_submitted"]:
        classification = "Manual Review"

    else:
        classification = "Eligible"

    return {
        "policy_id": policy_id,
        "policyholder_name": policy["holder_name"],
        "treatment": treatment,
        "claim_amount": claim_amount,
        "treatment_date": treatment_date,
        "classification": classification,
        "coverage_check": coverage_result,
        "document_check": documents_result,
        "amount_check": amount_result,
        "waiting_period_check": waiting_result,
        "rejection_reasons": rejection_reasons,
        "missing_documents": documents_result["missing_documents"],
        "message": (
            "Final recommendation generated by Python decision engine. "
            "Human reviewer must make the actual claim decision."
        )
    }
