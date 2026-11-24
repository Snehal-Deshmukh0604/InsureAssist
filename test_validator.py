
from utils.document_processor import process_pdf
from utils.document_validator import validate_documents


# Sample insurance claim details
policyholder_name = "Rahul Sharma"
claim_amount = 80000
treatment_date = "05-Jul-2024"

pdf_path = "hospital_bill.pdf"


# Process hospital bill
document_result = process_pdf(pdf_path)


if not document_result["success"]:

    print("\nDocument Processing Failed!")
    print(document_result["error"])

else:

    bill_details = document_result["bill_details"]

    # Validate extracted information
    validation = validate_documents(
        policyholder_name=policyholder_name,
        bill_details=bill_details,
        claim_amount=claim_amount,
        treatment_date=treatment_date
    )

    print("\n" + "=" * 60)
    print("           INSUREASSIST - DOCUMENT VALIDATION")
    print("=" * 60)

    print("\nPolicyholder :", policyholder_name)
    print("Claim Amount :", f"Rs. {claim_amount:,.2f}")
    print("Treatment Date:", treatment_date)

    print("\n" + "-" * 60)
    print("              VALIDATION RESULTS")
    print("-" * 60)

    for result in validation["validation_results"]:

        print(f"\nCheck  : {result['check']}")
        print(f"Status : {result['status']}")
        print(f"Result : {result['message']}")

    print("\n" + "=" * 60)
    print("OVERALL STATUS :", validation["overall_status"])
    print("=" * 60)
