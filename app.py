import streamlit as st
import pdfplumber
import re
from textblob import TextBlob

# --------------------------------------------------
# BASIC PAGE CONTENT (NO PAGE SETUP REQUIRED)
# --------------------------------------------------
st.title("Earnings Manipulation Risk Dashboard")
st.write(
    "Upload an Annual Report PDF. "
    "The system will automatically analyze the text and "
    "estimate the risk of earnings manipulation."
)

# --------------------------------------------------
# INPUT: PDF UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Annual Report (PDF only)",
    type=["pdf"]
)

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_section(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text[match.start():]
    return ""


def uncertainty_score(text):
    words = [
        "may", "might", "could", "expected",
        "subject to", "uncertain", "risk", "challenge"
    ]
    return sum(text.lower().count(w) for w in words) / max(len(text.split()), 1)

# --------------------------------------------------
# MAIN LOGIC
# --------------------------------------------------
if uploaded_file:

    if st.button("Analyze Report"):

        with st.spinner("Analyzing annual report..."):

            # 1. Read full PDF
            full_text = read_pdf(uploaded_file)

            # 2. Extract MD&A and Auditor sections
            mdna_text = extract_section(
                full_text,
                [
                    r"management discussion and analysis",
                    r"management discussion",
                    r"management review"
                ]
            )

            auditor_text = extract_section(
                full_text,
                [
                    r"independent auditors?[’']? report",
                    r"auditor[’']?s report"
                ]
            )

            # 3. Text analysis
            mdna_sentiment = TextBlob(mdna_text).sentiment.polarity
            auditor_sentiment = TextBlob(auditor_text).sentiment.polarity
            tone_gap = mdna_sentiment - auditor_sentiment
            mdna_uncertainty = uncertainty_score(mdna_text)

            # 4. REM risk score (text-based proxy)
            rem_score = (
                0.40 * abs(mdna_sentiment) +
                0.35 * mdna_uncertainty +
                0.25 * abs(tone_gap)
            ) * 100

        # --------------------------------------------------
        # OUTPUT
        # --------------------------------------------------
        st.subheader("Result")

        st.metric("REM Risk Score", round(rem_score, 2))

        if rem_score > 66:
            st.error("🔴 High Risk of Earnings Manipulation")
        elif rem_score > 33:
            st.warning("🟠 Moderate Risk of Earnings Manipulation")
        else:
            st.success("🟢 Low Risk of Earnings Manipulation")

        st.caption(
            "This output represents earnings manipulation risk based on "
            "narrative text patterns. It does not confirm manipulation."
        )
