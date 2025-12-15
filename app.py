import streamlit as st
import re

# --------------------------------------------------
# PAGE
# --------------------------------------------------
st.title("Earnings Manipulation Risk Dashboard")

st.write(
    "PDF → Text Analysis → REM Risk Output\n\n"
    "Upload an annual report PDF. The system analyzes management "
    "language patterns commonly associated with real earnings management."
)

# --------------------------------------------------
# FILE INPUT
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Annual Report (PDF)",
    type=["pdf"]
)

# --------------------------------------------------
# SIMPLE TEXT EXTRACTION (NO LIBRARIES)
# --------------------------------------------------
def extract_text_from_pdf(file):
    try:
        raw = file.read()
        text = raw.decode("latin-1", errors="ignore")
        return text.lower()
    except:
        return ""

# --------------------------------------------------
# DICTIONARY-BASED ANALYSIS (NO NLP LIBRARIES)
# --------------------------------------------------
positive_words = [
    "strong", "growth", "improved", "robust", "record", "positive"
]

uncertainty_words = [
    "may", "might", "could", "risk", "uncertain",
    "challenge", "subject to", "volatility"
]

justification_words = [
    "one-time", "exceptional", "temporary",
    "non-recurring", "adjusted", "excluding"
]

def score_text(text, word_list):
    return sum(text.count(w) for w in word_list)

# --------------------------------------------------
# MAIN LOGIC
# --------------------------------------------------
if uploaded_file:

    st.success("PDF uploaded successfully")

    if st.button("Analyze Report"):

        with st.spinner("Analyzing report text..."):

            text = extract_text_from_pdf(uploaded_file)

            if len(text.strip()) < 500:
                st.error(
                    "This PDF does not contain readable text. "
                    "Please upload a text-based annual report."
                )
                st.stop()

            pos_score = score_text(text, positive_words)
            unc_score = score_text(text, uncertainty_words)
            just_score = score_text(text, justification_words)

            # REM proxy score
            rem_score = (
                0.30 * pos_score +
                0.40 * unc_score +
                0.30 * just_score
            )

        # --------------------------------------------------
        # OUTPUT
        # --------------------------------------------------
        st.subheader("Result")

        st.metric("REM Risk Score", round(rem_score, 2))

        if rem_score > 150:
            st.error("🔴 High Risk of Earnings Manipulation")
        elif rem_score > 80:
            st.warning("🟠 Moderate Risk of Earnings Manipulation")
        else:
            st.success("🟢 Low Risk of Earnings Manipulation")

        st.caption(
            "The score is based on linguistic patterns "
            "linked to real earnings management in prior literature. "
            "This does not confirm manipulation."
        )
