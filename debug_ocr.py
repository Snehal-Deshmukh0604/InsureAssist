
from utils.document_processor import extract_text_from_pdf

pdf_path = r"D:\InsureAssist\scanned_hospital_bill_hd.pdf"

result = extract_text_from_pdf(pdf_path)

if result["success"]:

    for page in result["pages"]:

        print("\n========== OCR TEXT ==========\n")
        print(page["text"])

        print("\n========== LINE BY LINE ==========\n")

        for i, line in enumerate(page["text"].splitlines()):
            print(i, repr(line))

else:
    print("ERROR:", result["error"])
