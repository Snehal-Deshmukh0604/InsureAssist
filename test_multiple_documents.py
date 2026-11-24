
from utils.document_processor import process_multiple_pdfs


REQUIRED_DOCUMENTS = [
    "hospital bill",
    "discharge summary",
    "doctor prescription"
]


def display_multiple_document_report(results):

    print("\n" + "=" * 65)
    print("          INSUREASSIST - MULTIPLE DOCUMENT PROCESSING")
    print("=" * 65)

    detected_types = []

    for index, result in enumerate(results, start=1):

        print(f"\nDOCUMENT {index}")
        print("-" * 65)

        if not result["success"]:
            print("Processing Failed:", result["error"])
            continue

        print("File Name :", result["file_name"])
        print("Pages     :", result["page_count"])
        print("Status    : Successfully Processed")

        detected_documents = result["detected_documents"]

        if detected_documents:

            for document in detected_documents:

                document_type = document["document_type"]

                detected_types.append(document_type)

                print("Type      :", document_type.upper())

                if document_type == "hospital bill":

                    print("\nExtracted Bill Details:")

                    for field, value in result["bill_details"].items():
                        print(f"  {field:<22}: {value}")

        else:
            print("Type      : Unknown document")

    # Remove duplicate document types
    detected_types = list(set(detected_types))

    # Identify missing documents
    missing_documents = [
        document
        for document in REQUIRED_DOCUMENTS
        if document not in detected_types
    ]

    print("\n" + "=" * 65)
    print("              DOCUMENT CHECKLIST")
    print("=" * 65)

    for document in REQUIRED_DOCUMENTS:

        if document in detected_types:
            print(f"[FOUND]   {document.upper()}")
        else:
            print(f"[MISSING] {document.upper()}")

    print("\n" + "-" * 65)

    if missing_documents:
        print("DOCUMENT STATUS : INCOMPLETE")
        print("Missing Documents:")

        for document in missing_documents:
            print("-", document)

    else:
        print("DOCUMENT STATUS : COMPLETE")

    print("=" * 65)


if __name__ == "__main__":

    print("\n========== INSUREASSIST MULTIPLE DOCUMENT PROCESSOR ==========")

    print("\nEnter PDF file paths separated by commas.")
    print("Example: hospital_bill.pdf, discharge_summary.pdf")

    user_input = input("\nPDF Paths: ").strip()

    pdf_paths = [
        path.strip().strip('"')
        for path in user_input.split(",")
        if path.strip()
    ]

    results = process_multiple_pdfs(pdf_paths)

    display_multiple_document_report(results)
