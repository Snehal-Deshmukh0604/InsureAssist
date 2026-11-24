# InsureAssist – AI-Powered Health Insurance Claim Processing Agent

InsureAssist is an AI-powered health insurance claim processing prototype designed to simplify the initial assessment of health insurance claims. It analyzes uploaded medical documents, extracts relevant billing information, validates claim details, and generates a preliminary claim assessment report.

## 🚀 Features

- **PDF Document Processing:** Upload and process multiple digital PDF documents.
- **Document Identification:** Identifies hospital bills, OPD bills, and advance receipts.
- **AI-Based Information Extraction:** Uses Google Gemini AI to assist with claim information extraction and report generation.
- **Bill Details Extraction:** Extracts patient details, admission and discharge dates, bill amounts, discounts, and payment information.
- **Document Validation:** Checks patient identity, claimed amount against bill amount, and treatment dates.
- **Policy Eligibility Checking:** Evaluates policy coverage, claim limits, required documents, and waiting periods.
- **Automated Assessment Report:** Generates a preliminary claim recommendation with validation results and reasons.
- **Fallback Reporting:** Uses Python-based report generation when AI report generation is unavailable.
- **Streamlit Interface:** Provides a simple interface for uploading documents and viewing assessment results.

## 🛠️ Technologies Used

- Python
- Google Gemini API
- Streamlit
- PyMuPDF
- Pandas
- PyTesseract
- OpenCV
- Pillow

## ⚙️ Project Workflow

1. User enters insurance claim details and uploads PDF documents.
2. The system processes the uploaded PDFs.
3. It identifies document types and extracts hospital bill information.
4. Extracted details are validated against the submitted claim information.
5. Python-based rules evaluate policy coverage, claim limits, waiting periods, and required documents.
6. The system generates a preliminary claim assessment report.

## 📁 Project Structure

```text
InsureAssist/
│
├── app.py
├── agent.py
├── requirements.txt
├── .gitignore
│
└── utils/
    ├── tools.py
    ├── document_processor.py
    └── document_validator.py
```

## 💻 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/InsureAssist.git
cd InsureAssist
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never upload your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

## 🔮 Future Enhancements

- Improve OCR accuracy for scanned medical documents.
- Support additional medical document formats.
- Add more comprehensive policy rule validation.
- Improve the claim assessment dashboard.
- Integrate secure database storage and claim history.
- Add human reviewer feedback and approval workflows.

## ⚠️ Limitations and Disclaimer

- Currently designed as a prototype for health insurance claim assessment.
- Digital PDFs are the primary supported input. OCR-based processing of scanned documents is experimental and may not reliably extract all financial information.
- Sample policy and claim data are used for demonstration.
- The system generates preliminary recommendations only. It does not approve or reject real insurance claims.
- Final claim decisions must be made by an authorized human reviewer.

## 👩‍💻 Project Purpose

InsureAssist demonstrates how AI, document processing, and rule-based validation can be combined to automate parts of the health insurance claim assessment workflow.
