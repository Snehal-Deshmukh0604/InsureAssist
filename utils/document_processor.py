
import os
import re
import io
import pymupdf
import pytesseract
import cv2
import numpy as np

from PIL import Image


# =========================================================
# 1. OCR CONFIGURATION
# =========================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# =========================================================
# 2. IMAGE PREPROCESSING
# =========================================================

def preprocess_image(image):
    image_array = np.array(image)
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    denoised = cv2.fastNlMeansDenoising(
        gray, None, 10, 7, 21
    )

    return cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


# =========================================================
# 3. OCR QUALITY
# =========================================================

def calculate_text_quality(text):
    if not text:
        return 0

    alphanumeric = len(re.findall(r"[A-Za-z0-9]", text))
    total = len(text.strip())

    return alphanumeric / total if total else 0


# =========================================================
# 4. OCR EXTRACTION
# =========================================================

def extract_text_using_ocr(image):
    original_text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 3"
    )

    processed_image = preprocess_image(image)

    processed_text = pytesseract.image_to_string(
        processed_image,
        lang="eng",
        config="--oem 3 --psm 3"
    )

    if calculate_text_quality(processed_text) > calculate_text_quality(original_text):
        return processed_text

    return original_text


# =========================================================
# 5. PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(pdf_path: str):

    if not os.path.exists(pdf_path):
        return {"success": False, "error": f"File not found: {pdf_path}"}

    if not pdf_path.lower().endswith(".pdf"):
        return {"success": False, "error": "Only PDF files are supported."}

    if not os.path.isfile(TESSERACT_PATH):
        return {"success": False, "error": "Tesseract executable not found."}

    document = None

    try:
        document = pymupdf.open(pdf_path)

        pages = []
        pages_text = []
        ocr_pages = []
        ocr_errors = []

        for page_number, page in enumerate(document, start=1):

            page_text = page.get_text("text", sort=True)

            meaningful_characters = len(
                re.sub(r"[^A-Za-z0-9]", "", page_text)
            )

            extraction_method = "text"

            if meaningful_characters < 30:

                extraction_method = "ocr"

                try:
                    pixmap = page.get_pixmap(dpi=300, alpha=False)

                    image_bytes = pixmap.tobytes("png")

                    image = Image.open(
                        io.BytesIO(image_bytes)
                    ).convert("RGB")

                    page_text = extract_text_using_ocr(image)

                    image.close()
                    ocr_pages.append(page_number)

                except Exception as ocr_error:
                    ocr_errors.append({
                        "page_number": page_number,
                        "error": str(ocr_error)
                    })

            pages.append({
                "page_number": page_number,
                "text": page_text,
                "extraction_method": extraction_method
            })

            pages_text.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

        return {
            "success": True,
            "file_name": os.path.basename(pdf_path),
            "page_count": len(document),
            "pages": pages,
            "extracted_text": "\n\n".join(pages_text),
            "ocr_pages": ocr_pages,
            "ocr_page_count": len(ocr_pages),
            "ocr_errors": ocr_errors
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        if document is not None:
            document.close()


# =========================================================
# 6. BASIC HELPERS
# =========================================================

def clean_value(value):

    if not value:
        return None

    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" :.-")

    if not value or value.lower() in [
        "none", "n/a", "na", "not available"
    ]:
        return None

    return value


def normalize_lines(text):

    text = text.replace("\u200b", "").replace("\ufeff", "")

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def compact_text(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


AMOUNT_PATTERN = (
    r"(?:₹|Rs\.?\s*)?"
    r"\d[\d,]*(?:\.\d{1,2})?"
)

DATE_PATTERN = (
    r"\d{1,2}[-/]"
    r"(?:\d{1,2}|[A-Za-z]{3,9})"
    r"[-/]\d{2,4}"
)


def convert_amount(amount):

    if not amount:
        return None

    cleaned = re.sub(r"[^\d.]", "", str(amount))

    try:
        return float(cleaned)
    except ValueError:
        return None


# =========================================================
# 7. FILLED DOCUMENT CHECKS
# =========================================================

def has_filled_value(text, label_patterns):

    for pattern in label_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )

        if match:
            value = match.group(1).strip()

            if value and re.search(r"[A-Za-z0-9]", value):
                return True

    return False


def is_filled_bill_page(text):

    has_bill_number = has_filled_value(text, [
        r"Bill\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)",
        r"Invoice\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)"
    ])

    has_patient_name = has_filled_value(text, [
        r"Patient'?s?\s+name\s*[:.]?\s*([A-Za-z][A-Za-z .'-]{1,})",
        r"^Name\s*[:.]?\s*([A-Za-z][A-Za-z .'-]{1,})"
    ])

    has_amount = bool(re.search(
        r"(?:Total of all charges|Bill amount|Grand Total|"
        r"Net Amount|Total Amount|^\s*Total)\s*[:.]?\s*"
        + AMOUNT_PATTERN,
        text,
        flags=re.IGNORECASE | re.MULTILINE
    ))

    return sum([
        has_bill_number,
        has_patient_name,
        has_amount
    ]) >= 2


def is_filled_receipt_page(text):

    has_receipt_number = has_filled_value(text, [
        r"Receipt\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)"
    ])

    has_patient_name = has_filled_value(text, [
        r"Patient'?s?\s+name\s*[:.]?\s*([A-Za-z][A-Za-z .'-]{1,})"
    ])

    has_received_amount = bool(re.search(
        r"Amount\s+received\s*[:.]?\s*" + AMOUNT_PATTERN,
        text,
        flags=re.IGNORECASE
    ))

    return sum([
        has_receipt_number,
        has_patient_name,
        has_received_amount
    ]) >= 2


# =========================================================
# 8. DOCUMENT IDENTIFICATION
# =========================================================

def identify_document(extracted_text: str):

    text = re.sub(r"\s+", " ", extracted_text.lower())
    compact = compact_text(extracted_text)

    detected_documents = []

    # Advance receipt

    advance_heading_found = (
        "advancereceipt" in compact
        or "receiptvoucher" in compact
    )

    advance_keywords = [
        "advance receipt",
        "receipt voucher",
        "advance payment"
    ]

    matched_advance = [
        keyword for keyword in advance_keywords
        if keyword in text
    ]

    if advance_heading_found and is_filled_receipt_page(extracted_text):

        if not matched_advance:
            matched_advance = ["advance receipt"]

        detected_documents.append({
            "document_type": "advance receipt",
            "matched_keywords": matched_advance
        })

        return detected_documents

    # OPD bill

    if "opdbill" in compact:

        if is_filled_bill_page(extracted_text):
            detected_documents.append({
                "document_type": "OPD bill",
                "matched_keywords": ["opd bill"]
            })

        return detected_documents

    # Hospital bill

    hospital_keywords = [
        "hospital bill",
        "medical bill",
        "medical bill receipt",
        "final bill",
        "hospital invoice",
        "patient invoice",
        "billing details",
        "total amount",
        "total of all charges",
        "bill amount",
        "net amount",
        "bill no",
        "invoice no"
    ]

    matched_hospital = [
        keyword for keyword in hospital_keywords
        if keyword in text
    ]

    strong_headings = [
        "final bill",
        "medical bill receipt",
        "hospital bill",
        "hospital invoice"
    ]

    has_heading = any(
        heading in text for heading in strong_headings
    )

    if (
        (has_heading or len(matched_hospital) >= 2)
        and is_filled_bill_page(extracted_text)
    ):

        detected_documents.append({
            "document_type": "hospital bill",
            "matched_keywords": matched_hospital
        })

        return detected_documents

    # Discharge summary

    discharge_keywords = [
        "discharge summary",
        "discharge diagnosis",
        "final diagnosis",
        "clinical summary",
        "treatment summary",
        "date of discharge",
        "condition at discharge",
        "advice on discharge"
    ]

    matched = [
        keyword for keyword in discharge_keywords
        if keyword in text
    ]

    if len(matched) >= 2:
        detected_documents.append({
            "document_type": "discharge summary",
            "matched_keywords": matched
        })

    # Doctor prescription

    prescription_keywords = [
        "doctor prescription",
        "prescription",
        "medicines prescribed",
        "prescribed medication",
        "rx:",
        "dosage",
        "prescribed by"
    ]

    matched = [
        keyword for keyword in prescription_keywords
        if keyword in text
    ]

    if len(matched) >= 2:
        detected_documents.append({
            "document_type": "doctor prescription",
            "matched_keywords": matched
        })

    # Lab report

    lab_keywords = [
        "laboratory report",
        "lab report",
        "test report",
        "investigation report",
        "blood test",
        "test result",
        "reference range"
    ]

    matched = [
        keyword for keyword in lab_keywords
        if keyword in text
    ]

    if len(matched) >= 2:
        detected_documents.append({
            "document_type": "lab report",
            "matched_keywords": matched
        })

    # Diagnostic report

    diagnostic_keywords = [
        "radiology report",
        "x-ray report",
        "mri report",
        "ct scan report",
        "ultrasound report",
        "imaging report"
    ]

    matched = [
        keyword for keyword in diagnostic_keywords
        if keyword in text
    ]

    if len(matched) >= 1:
        detected_documents.append({
            "document_type": "diagnostic report",
            "matched_keywords": matched
        })

    return detected_documents


# =========================================================
# 9. PATIENT NAME EXTRACTION
# =========================================================

def extract_patient_name(lines):

    for line in lines:

        match = re.search(
            r"Patient'?s?\s+name\s*[:.]?\s*(.*)",
            line,
            flags=re.IGNORECASE
        )

        if not match:
            match = re.search(
                r"\bName\s*[:.]?\s*(.*)",
                line,
                flags=re.IGNORECASE
            )

        if not match:
            continue

        candidate = match.group(1)

        candidate = re.split(
            r"\bAge and sex\b|\bUHID\b|\bIP number\b",
            candidate,
            flags=re.IGNORECASE
        )[0]

        candidate = clean_value(candidate)

        if candidate and re.fullmatch(
            r"[A-Za-z][A-Za-z .'-]{1,60}",
            candidate
        ):
            return candidate

    return None


# =========================================================
# 10. DOCUMENT NUMBER EXTRACTION
# =========================================================

def extract_document_number(lines):

    patterns = [
        r"Bill\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)",
        r"Invoice\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)",
        r"Receipt\s+no\.?\s*[:.]?\s*([A-Za-z0-9/-]+)"
    ]

    for pattern in patterns:

        for line in lines:

            match = re.search(
                pattern,
                line,
                flags=re.IGNORECASE
            )

            if match:
                value = clean_value(match.group(1))

                if value and re.search(r"\d", value):
                    return value

    return None


# =========================================================
# 11. DATE EXTRACTION
# =========================================================

def extract_date(text, labels):

    for label in labels:

        pattern = (
            label
            + r"\s*[:.]?\s*("
            + DATE_PATTERN
            + r")"
        )

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# 12. FINANCIAL AMOUNT EXTRACTION
# =========================================================

FINANCIAL_LABELS = [
    r"Total\s+of\s+all\s+charges",
    r"Gross\s+Total",
    r"Total\s+Charges",
    r"Less\s+discount",
    r"Discount",
    r"Bill\s+amount",
    r"Final\s+Amount",
    r"Grand\s+Total",
    r"Net\s+Amount",
    r"Total\s+Amount",
    r"Insurer'?s?\s+share",
    r"Insurance\s+Coverage",
    r"Insurance\s+Share",
    r"Paid\s+at\s+discharge",
    r"Patient\s+Payment",
    r"Advance\s+paid",
    r"Balance\s+due"
]


def extract_amount_candidates(text):

    # Remove dates so date components are not read as amounts.
    text = re.sub(
        DATE_PATTERN,
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Extract numeric monetary values.
    return re.findall(AMOUNT_PATTERN, text)


def extract_amount_by_label(text, labels):

    lines = normalize_lines(text)

    for label in labels:

        for index, line in enumerate(lines):

            match = re.search(
                label,
                line,
                flags=re.IGNORECASE
            )

            if not match:
                continue

            # Search after the label on the same line.
            remaining_text = line[match.end():]

            amounts = extract_amount_candidates(remaining_text)

            if amounts:
                return amounts[-1]

            # Search nearby lines, allowing intervening text.
            # Stop when another financial label begins.
            for next_line in lines[index + 1:index + 6]:

                another_label_found = any(
                    re.search(
                        other_label,
                        next_line,
                        flags=re.IGNORECASE
                    )
                    for other_label in FINANCIAL_LABELS
                )

                if another_label_found:
                    break

                amounts = extract_amount_candidates(next_line)

                if amounts:
                    return amounts[-1]

    return None


# =========================================================
# 13. EXTRACT BILL DETAILS
# =========================================================

def extract_bill_details(extracted_text: str):

    lines = normalize_lines(extracted_text)

    patient_name = extract_patient_name(lines)
    receipt_number = extract_document_number(lines)

    admission_date = extract_date(
        extracted_text,
        [
            r"Date of Admission",
            r"Admission Date",
            r"Admitted"
        ]
    )

    discharge_date = extract_date(
        extracted_text,
        [
            r"Date of Discharge",
            r"Discharge Date",
            r"Discharged"
        ]
    )

    gross_total = extract_amount_by_label(
        extracted_text,
        [
            r"Total\s+of\s+all\s+charges",
            r"Gross\s+Total",
            r"Total\s+Charges"
        ]
    )

    discount = extract_amount_by_label(
        extracted_text,
        [
            r"Less\s+discount",
            r"Discount"
        ]
    )

    total_amount = extract_amount_by_label(
        extracted_text,
        [
            r"Bill\s+amount",
            r"Final\s+Amount",
            r"Grand\s+Total",
            r"Net\s+Amount",
            r"Total\s+Amount"
        ]
    )

    insurance_coverage = extract_amount_by_label(
        extracted_text,
        [
            r"Insurer'?s?\s+share",
            r"Insurance\s+Coverage",
            r"Insurance\s+Share"
        ]
    )

    patient_payment = extract_amount_by_label(
        extracted_text,
        [
            r"Paid\s+at\s+discharge",
            r"Patient\s+Payment"
        ]
    )

    advance_paid = extract_amount_by_label(
        extracted_text,
        [
            r"Advance\s+paid"
        ]
    )

    balance_due = extract_amount_by_label(
        extracted_text,
        [
            r"Balance\s+due"
        ]
    )

    return {
        "patient_name": patient_name,
        "receipt_number": receipt_number,
        "admission_date": admission_date,
        "discharge_date": discharge_date,
        "gross_total_amount": convert_amount(gross_total),
        "discount_amount": convert_amount(discount),
        "total_amount": convert_amount(total_amount),
        "insurance_coverage": convert_amount(insurance_coverage),
        "advance_paid_amount": convert_amount(advance_paid),
        "patient_payment": convert_amount(patient_payment),
        "balance_due": convert_amount(balance_due)
    }


# =========================================================
# 14. PROCESS SINGLE PDF
# =========================================================

def process_pdf(pdf_path: str):

    extraction_result = extract_text_from_pdf(pdf_path)

    if not extraction_result["success"]:
        return extraction_result

    extracted_text = extraction_result["extracted_text"]

    page_wise_documents = []

    hospital_bill_text = None
    opd_bill_text = None

    for page in extraction_result["pages"]:

        page_number = page["page_number"]
        page_text = page["text"]

        detected = identify_document(page_text)

        for document in detected:

            document_type = document["document_type"]

            page_wise_documents.append({
                "page_number": page_number,
                "document_type": document_type,
                "matched_keywords": document["matched_keywords"],
                "extraction_method": page["extraction_method"]
            })

            if (
                document_type == "hospital bill"
                and hospital_bill_text is None
            ):
                hospital_bill_text = page_text

            elif (
                document_type == "OPD bill"
                and opd_bill_text is None
            ):
                opd_bill_text = page_text

    selected_bill_text = (
        hospital_bill_text
        if hospital_bill_text
        else opd_bill_text
    )

    if selected_bill_text:
        bill_details = extract_bill_details(selected_bill_text)

    else:
        bill_details = {
            "patient_name": None,
            "receipt_number": None,
            "admission_date": None,
            "discharge_date": None,
            "gross_total_amount": None,
            "discount_amount": None,
            "total_amount": None,
            "insurance_coverage": None,
            "advance_paid_amount": None,
            "patient_payment": None,
            "balance_due": None
        }

    return {
        "success": True,
        "file_name": extraction_result["file_name"],
        "page_count": extraction_result["page_count"],
        "detected_documents": page_wise_documents,
        "bill_details": bill_details,
        "extracted_text": extracted_text,
        "ocr_pages": extraction_result["ocr_pages"],
        "ocr_page_count": extraction_result["ocr_page_count"],
        "ocr_errors": extraction_result["ocr_errors"]
    }


# =========================================================
# 15. PROCESS MULTIPLE PDFs
# =========================================================

def process_multiple_pdfs(pdf_paths: list):

    results = []

    for pdf_path in pdf_paths:
        result = process_pdf(pdf_path)
        results.append(result)

    return {
        "success": True,
        "total_files": len(pdf_paths),
        "results": results
    }
