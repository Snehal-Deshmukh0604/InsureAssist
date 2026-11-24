
from utils.tools import (
    get_policy_details,
    check_coverage,
    check_required_documents,
    check_claim_amount,
    check_waiting_period
)

print("\n--- POLICY DETAILS ---")
print(get_policy_details("INS1001"))

print("\n--- COVERAGE CHECK ---")
print(check_coverage("INS1001", "hospitalization"))

print("\n--- DOCUMENT CHECK ---")
print(
    check_required_documents(
        "INS1001",
        ["hospital bill"]
    )
)

print("\n--- CLAIM AMOUNT CHECK ---")
print(check_claim_amount("INS1001", 80000))
print("\n--- WAITING PERIOD CHECK ---")
print(check_waiting_period("INS1001", "2026-06-15"))