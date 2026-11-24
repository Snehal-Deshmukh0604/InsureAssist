
from utils.document_processor import process_pdf


def display_document_report(result):

    print("\n" + "=" * 60)
    print("             INSUREASSIST - DOCUMENT ANALYSIS")
    print("=" * 60)

    if not result["success"]:
        print("\n[ERROR]", result["error"])
        return

    print(f"\nFile Name   : {result['file_name']}")
    print(f"Total Pages : {result['page_count']}")
    print("Status      : Successfully Processed")

    # DOCUMENT IDENTIFICATION
    print("\n" + "-" * 60)
    print("              DOCUMENT IDENTIFICATION")
    print("-" * 60)

    detected = result["detected_documents"]

    if detected:
        for index, document in enumerate(detected, start=1):

            print(
    f"\n{index}. {document['document_type'].upper()} "
    f"(Page {document['page_number']})"
)
            print("   Matched Keywords:")

            for keyword in document["matched_keywords"]:
                print(f"   - {keyword}")

    else:
        print("\nNo known document type detected.")

    # EXTRACTED BILL DETAILS
    print("\n" + "-" * 60)
    print("             EXTRACTED BILL DETAILS")
    print("-" * 60)

    details = result["bill_details"]

    field_labels = {
        "patient_name": "Patient Name",
        "receipt_number": "Receipt Number",
        "admission_date": "Admission Date",
        "discharge_date": "Discharge Date",
        "gross_total_amount": "Gross Total",
        "discount_amount": "Discount",
        "total_amount": "Final Bill Amount",
        "insurance_coverage": "Insurance Coverage",
        "patient_payment": "Patient Payment"
    }

    amount_fields = [
        "gross_total_amount",
        "discount_amount",
        "total_amount",
        "insurance_coverage",
        "patient_payment"
    ]

    for field, label in field_labels.items():

        value = details.get(field)

        if value is None:
            value = "Not Found"

        elif field in amount_fields:
            value = f"Rs. {value:,.2f}"

        print(f"{label:<22}: {value}")

    print("\n" + "=" * 60)
    print("              END OF DOCUMENT REPORT")
    print("=" * 60)


if __name__ == "__main__":

    print("\n========== INSUREASSIST DOCUMENT PROCESSOR ==========")

    pdf_path = input("\nEnter PDF file path: ").strip().strip('"')

    result = process_pdf(pdf_path)

    display_document_report(result)
