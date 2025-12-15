import streamlit as st
import re

# ==================================================
# PAGE
# ==================================================
st.title("Earnings Manipulation Risk Dashboard")

st.write(
    """
    **Stakeholder View**  
    Input: Annual Report PDF  
    Output: Earnings Manipulation Risk  

    The system automatically detects real earnings management (REM)
    indicators from narrative and numerical patterns in the report.
    """
)

# ==================================================
# PDF INPUT
# ==================================================
uploaded_file = st.file_uploader(
    "Upload Annual Report (PDF)",
    type=["pdf"]
)

# ==================================================
# BASIC PDF TEXT EXTRACTION (PURE PYTHON)
# ==================================================
def extract_text_from_pdf(file):
    try:
        raw = file.read()
        return raw.decode("latin-1", errors="ignore").lower()
    except:
        return ""

# ==================================================
# TEXTUAL REM SIGNALS
# ==================================================
optimism_words = [
    "strong", "record", "robust", "exceptional",
    "resilient", "growth", "outperformance"
]

uncertainty_words = [
    "may", "might", "could", "risk", "uncertain",
    "challenge", "headwinds", "volatility"
]

justification_words = [
    "one-time", "exceptional", "temporary",
    "non-recurring", "adjusted", "excluding"
]

def word_score(text, words):
    return sum(text.count(w) for w in words)

# ==================================================
# AUTO NUMERIC DETECTION (HEURISTIC)
# ==================================================
def detect_large_numbers(text):
    # detects large financial-looking numbers (₹, $, millions, crores etc.)
    pattern = r"(rs\.?|₹|\$)?\s?\d{2,}(?:,\d{2,})*(?:\.\d+)?"
    numbers = re.findall(pattern, text)
    return len(numbers)

def detect_financial_activity(text, keywords):
    return sum(text.count(k) for k in keywords)

# ==================================================
# MAIN ANALYSIS
# ==================================================
if uploaded_file and st.button("Analyze Report"):

    with st.spinner("Analyzing report automatically..."):

        text = extract_text_from_pdf(uploaded_file)

        if len(text.strip()) < 1000:
            st.error("PDF does not contain sufficient readable text.")
            st.stop()

        # ---------------- TEXT REM SCORE ----------------
        optimism = word_score(text, optimism_words)
        uncertainty = word_score(text, uncertainty_words)
        justification = word_score(text, justification_words)

        text_rem_score = (
            0.35 * optimism +
            0.40 * uncertainty +
            0.25 * justification
        )

        # ---------------- NUMERIC REM PROXIES ----------------
        large_numbers = detect_large_numbers(text)

        inventory_mentions = detect_financial_activity(
            text, ["inventory", "stock", "raw material"]
        )

        receivable_mentions = detect_financial_activity(
            text, ["receivable", "debtor", "outstanding"]
        )

        cashflow_mentions = detect_financial_activity(
            text, ["cash flow", "operating cash", "cfo"]
        )

        capex_mentions = detect_financial_activity(
            text, ["capital expenditure", "capex", "investment"]
        )

        numeric_rem_score = (
            0.25 * large_numbers +
            0.20 * inventory_mentions +
            0.20 * receivable_mentions +
            0.20 * capex_mentions +
            0.15 * (1 / (cashflow_mentions + 1))
        )

        # ---------------- FINAL SCORE ----------------
        final_score = (0.55 * numeric_rem_score) + (0.45 * text_rem_score)

    # ==================================================
    # OUTPUT
    # ==================================================
    st.subheader("Results")

    st.metric("Text-based REM Signal", round(text_rem_score, 2))
    st.metric("Numeric REM Signal", round(numeric_rem_score, 2))
    st.metric("Final Manipulation Risk Score", round(final_score, 2))

    if final_score > 120:
        st.error("🔴 High Risk of Earnings Manipulation")
    elif final_score > 70:
        st.warning("🟠 Moderate Risk of Earnings Manipulation")
    else:
        st.success("🟢 Low Risk of Earnings Manipulation")

    st.caption(
        "The dashboard automatically infers REM indicators from "
        "narrative tone and financial activity patterns. "
        "This is a risk signal, not an audit conclusion."
    )
