
from datetime import datetime


def normalize_name(name):
    """Normalize names before comparison."""

    if not name:
        return ""

    return " ".join(name.lower().strip().split())


def parse_date(date_value):
    """Convert supported date formats into date objects."""

    if not date_value:
        return None

    formats = [
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y"
    ]

    for date_format in formats:
        try:
            return datetime.strptime(
                date_value.strip(),
                date_format
            ).date()
        except ValueError:
            continue

    return None


def validate_documents(
    policyholder_name,
    bill_details,
    claim_amount,
    treatment_date=None
):
    """
    Compare extracted hospital bill information
    with the submitted insurance claim.
    """

    validation_results = []

    # 1. Patient Identity Validation

    patient_name = bill_details.get("patient_name")

    if not patient_name:
        validation_results.append({
            "check": "Patient Identity",
            "status": "REVIEW",
            "message": "Patient name is missing from the hospital bill."
        })

    elif normalize_name(patient_name) == normalize_name(policyholder_name):
        validation_results.append({
            "check": "Patient Identity",
            "status": "PASS",
            "message": "Patient name matches the policyholder."
        })

    else:
        validation_results.append({
            "check": "Patient Identity",
            "status": "REVIEW",
            "message": (
                f"Policyholder: {policyholder_name}, "
                f"Bill Patient: {patient_name}. "
                "Identity mismatch detected."
            )
        })

    # 2. Claim Amount Validation

    bill_amount = bill_details.get("total_amount")

    if bill_amount is None:
        validation_results.append({
            "check": "Claim Amount",
            "status": "REVIEW",
            "message": "Total bill amount could not be extracted."
        })

    elif claim_amount is None or claim_amount < 0:
        validation_results.append({
            "check": "Claim Amount",
            "status": "REVIEW",
            "message": "Claim amount is missing or invalid."
        })

    elif claim_amount > bill_amount:
        validation_results.append({
            "check": "Claim Amount",
            "status": "REVIEW",
            "message": (
                f"Claim amount Rs. {claim_amount:,.2f} "
                f"exceeds bill amount Rs. {bill_amount:,.2f}."
            )
        })

    else:
        validation_results.append({
            "check": "Claim Amount",
            "status": "PASS",
            "message": (
                f"Claim amount Rs. {claim_amount:,.2f} "
                f"is within the total bill amount "
                f"Rs. {bill_amount:,.2f}."
            )
        })

    # 3. Treatment Date Validation

    if treatment_date:

        admission_date = parse_date(
            bill_details.get("admission_date")
        )

        discharge_date = parse_date(
            bill_details.get("discharge_date")
        )

        treatment = parse_date(treatment_date)

        if not admission_date or not discharge_date or not treatment:

            validation_results.append({
                "check": "Treatment Date",
                "status": "REVIEW",
                "message": "One or more dates are missing or invalid."
            })

        elif admission_date <= treatment <= discharge_date:

            validation_results.append({
                "check": "Treatment Date",
                "status": "PASS",
                "message": "Treatment date falls within the hospital stay."
            })

        else:

            validation_results.append({
                "check": "Treatment Date",
                "status": "REVIEW",
                "message": "Treatment date does not fall within the hospital stay."
            })

    # 4. Overall Validation Status

    all_passed = all(
        result["status"] == "PASS"
        for result in validation_results
    )

    overall_status = "PASSED" if all_passed else "MANUAL REVIEW"

    return {
        "overall_status": overall_status,
        "validation_results": validation_results
    }
