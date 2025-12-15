import streamlit as st
import re

# ==================================================
# PAGE
# ==================================================
st.title("Earnings Manipulation Risk Dashboard")

st.write(
    """
    **Input:** Annual Report PDF + Financial Statement Numbers  
    **Process:** Text Analysis + Real Earnings Management (REM) Indicators  
    **Output:** Manipulation Risk Classification
    """
)

# ==================================================
# PDF INPUT
# ==================================================
uploaded_file = st.file_uploader(
    "Upload Annual Report (text-based PDF)",
    type=["pdf"]
)

def extract_text_from_pdf(file):
    try:
        raw = file.read()
        return raw.decode("latin-1", errors="ignore").lower()
    except:
        return ""

# ==================================================
# TEXT-BASED REM SIGNALS (DICTIONARY METHOD)
# ==================================================
positive_words = [
    "strong", "growth", "record", "robust",
    "improved", "positive", "resilient"
]

uncertainty_words = [
    "may", "might", "could", "risk",
    "uncertain", "challenge", "volatility"
]

justification_words = [
    "one-time", "exceptional", "temporary",
    "non-recurring", "adjusted", "excluding"
]

def count_words(text, word_list):
    return sum(text.count(w) for w in word_list)

# ==================================================
# FINANCIAL INPUTS (3 STATEMENTS)
# ==================================================
st.subheader("Enter Financial Statement Data")

revenue = st.number_input("Revenue", min_value=0.0)
net_profit = st.number_input("Net Profit")
cash_flow_ops = st.number_input("Cash Flow from Operations (CFO)")
inventory = st.number_input("Inventory")
receivables = st.number_input("Trade Receivables")
capex = st.number_input("Capital Expenditure")

# ==================================================
# ANALYSIS
# ==================================================
if uploaded_file and st.button("Analyze Report"):

    # ---------------- PDF TEXT ANALYSIS ----------------
    text = extract_text_from_pdf(uploaded_file)

    if len(text.strip()) < 500:
        st.error("PDF does not contain readable text.")
        st.stop()

    pos_score = count_words(text, positive_words)
    unc_score = count_words(text, uncertainty_words)
    just_score = count_words(text, justification_words)

    text_rem_score = (
        0.3 * pos_score +
        0.4 * unc_score +
        0.3 * just_score
    )

    # ---------------- NUMERICAL REM ANALYSIS ----------------
    if revenue <= 0:
        st.error("Revenue must be greater than zero.")
        st.stop()

    cfo_gap = abs(net_profit - cash_flow_ops) / revenue
    inventory_ratio = inventory / revenue
    receivable_ratio = receivables / revenue
    capex_ratio = capex / revenue

    numeric_rem_score = (
        0.35 * cfo_gap +
        0.25 * inventory_ratio +
        0.20 * receivable_ratio +
        0.20 * capex_ratio
    ) * 100

    # ---------------- FINAL COMBINED SCORE ----------------
    final_rem_score = (0.6 * numeric_rem_score) + (0.4 * text_rem_score)

    # ==================================================
    # OUTPUT
    # ==================================================
    st.subheader("Results")

    st.metric("Text-based REM Score", round(text_rem_score, 2))
    st.metric("Numeric REM Score", round(numeric_rem_score, 2))
    st.metric("Final REM Risk Score", round(final_rem_score, 2))

    if final_rem_score > 80:
        st.error("🔴 High Risk of Earnings Manipulation")
    elif final_rem_score > 40:
        st.warning("🟠 Moderate Risk of Earnings Manipulation")
    else:
        st.success("🟢 Low Risk of Earnings Manipulation")

    st.caption(
        "The assessment combines narrative disclosure patterns and "
        "financial-statement-based REM indicators. "
        "It signals risk, not proof of manipulation."
    )
