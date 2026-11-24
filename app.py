
import os
import tempfile
import traceback
import streamlit as st

from agent import assess_claim


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="InsureAssist",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# HEADER
# ==========================================

st.title("🏥 InsureAssist")
st.subheader("Intelligent Insurance Claim Processing System")

st.write(
    "Upload insurance claim details and supporting documents "
    "to generate an automated preliminary claim assessment."
)

st.info(
    "This application generates recommendations for human reviewers. "
    "It does not approve or reject actual insurance claims."
)

st.divider()


# ==========================================
# CLAIM SUBMISSION FORM
# ==========================================

st.header("Submit Insurance Claim")

with st.form("claim_form"):

    col1, col2 = st.columns(2)

    with col1:
        policy_id = st.selectbox(
            "Select Policy ID",
            ["INS1001", "INS1002"]
        )

        treatment = st.selectbox(
            "Treatment Type",
            [
                "hospitalization",
                "surgery",
                "accident",
                "medical treatment",
                "cosmetic surgery",
                "experimental treatment"
            ]
        )

    with col2:
        claim_amount = st.number_input(
            "Claim Amount (₹)",
            min_value=0.0,
            value=80000.0,
            step=1000.0
        )

        treatment_date = st.date_input("Treatment Date")

    st.subheader("Upload Supporting Documents")

    uploaded_files = st.file_uploader(
        "Upload hospital bill, discharge summary and prescription",
        type=["pdf"],
        accept_multiple_files=True
    )

    submit_button = st.form_submit_button(
        "Assess Insurance Claim",
        use_container_width=True
    )


# ==========================================
# CLAIM PROCESSING
# ==========================================

if submit_button:

    if claim_amount <= 0:
        st.error("Please enter a valid claim amount.")

    elif not uploaded_files:
        st.warning("Please upload at least one PDF document.")

    else:

        claim_details = f"""
        Please assess this insurance claim.

        Policy ID: {policy_id}
        Treatment: {treatment}
        Claim Amount: {claim_amount}
        Treatment Date: {treatment_date}

        Submitted Documents: []
        """

        with st.spinner(
            "Processing documents and assessing insurance claim..."
        ):

            try:

                with tempfile.TemporaryDirectory() as temp_dir:

                    pdf_paths = []

                    for index, uploaded_file in enumerate(uploaded_files):

                        file_path = os.path.join(
                            temp_dir,
                            f"{index}_{os.path.basename(uploaded_file.name)}"
                        )

                        with open(file_path, "wb") as file:
                            file.write(uploaded_file.getbuffer())

                        pdf_paths.append(file_path)

                    result = assess_claim(
                        claim_details,
                        pdf_paths=pdf_paths
                    )

                st.session_state["assessment_result"] = result

            except Exception as error:

                st.error(f"An error occurred: {error}")

                st.subheader("Detailed Error Traceback")

                st.exception(error)

                print("\n========== INSUREASSIST ERROR ==========")
                traceback.print_exc()
                print("=========================================\n")


# ==========================================
# DISPLAY ASSESSMENT REPORT
# ==========================================

if "assessment_result" in st.session_state:

    st.divider()

    st.header("📋 Claim Assessment Report")

    st.markdown(
        st.session_state["assessment_result"]
    )

    st.divider()

    st.caption(
        "InsureAssist | AI-assisted insurance claim assessment "
        "| Final decisions require human review."
    )
