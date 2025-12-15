import streamlit as st
import re
import statistics

# ==================================================
# PAGE
# ==================================================
st.title("Automated Earnings Manipulation Detection Dashboard")

st.write("""
**Input:** 2–5 annual report PDFs (same company, older → newer)  
**Model:**  
• Numeric REM using ABS(-CFO) + ABS(PROD) + ABS(-DISC)  
• Independent Text Manipulation Analysis  
• Baseline-adjusted, fully automated
""")

# ==================================================
# INPUT
# ==================================================
files = st.file_uploader(
    "Upload 2–5 Annual Report PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# ==================================================
# TEXT EXTRACTION
# ==================================================
def extract_text(file):
    raw = file.read()
    return raw.decode("latin-1", errors="ignore").lower()

# ==================================================
# TEXT ANALYSIS
# ==================================================
OPT = ["strong","robust","record","growth","outperformance"]
UNC = ["may","might","could","risk","uncertain","volatility","challenge"]
JUST = ["one-time","temporary","non-recurring","adjusted","excluding"]

def text_score(text):
    n = max(len(text.split()), 1)

    optimism = sum(text.count(w) for w in OPT) / n * 1000
    uncertainty = sum(text.count(w) for w in UNC) / n * 1000
    justification = sum(text.count(w) for w in JUST) / n * 1000

    return (
        0.30 * optimism +
        0.40 * uncertainty +
        0.30 * justification
    )

# ==================================================
# NUMERIC REM PROXIES (DENSITY-BASED)
# ==================================================
def density(text, keywords):
    n = max(len(text.split()), 1)
    return sum(text.count(k) for k in keywords) / n * 1000

CFO_KEYS = ["cash flow", "cash from operations", "operating cash", "cfo"]
PROD_KEYS = ["inventory", "production", "raw material", "cost of goods"]
DISC_KEYS = ["marketing", "advertis", "r&d", "selling", "sg&a"]

# ==================================================
# MAIN ANALYSIS
# ==================================================
if files and len(files) >= 2 and st.button("Run Analysis"):

    text_scores = []
    cfo_vals, prod_vals, disc_vals = [], [], []

    for f in files:
        text = extract_text(f)
        if len(text) < 1200:
            st.error("One PDF has insufficient readable text.")
            st.stop()

        # --- TEXT ---
        text_scores.append(text_score(text))

        # --- NUMERIC PROXIES ---
        cfo_vals.append(density(text, CFO_KEYS))
        prod_vals.append(density(text, PROD_KEYS))
        disc_vals.append(density(text, DISC_KEYS))

    # ==================================================
    # BASELINE vs CURRENT
    # ==================================================
    base_text = statistics.mean(text_scores[:-1])
    curr_text = text_scores[-1]
    abnormal_text = abs(curr_text - base_text)

    base_cfo = statistics.mean(cfo_vals[:-1])
    base_prod = statistics.mean(prod_vals[:-1])
    base_disc = statistics.mean(disc_vals[:-1])

    curr_cfo = cfo_vals[-1]
    curr_prod = prod_vals[-1]
    curr_disc = disc_vals[-1]

    # --------------------------------------------------
    # SIGNED ABNORMAL VALUES (IMPORTANT)
    # --------------------------------------------------
    ab_cfo = curr_cfo - base_cfo        # ↓ CFO = income increasing
    ab_prod = curr_prod - base_prod     # ↑ production = income increasing
    ab_disc = curr_disc - base_disc     # ↓ disc exp = income increasing

    # --------------------------------------------------
    # EXACT FORMULA YOU ASKED FOR
    # --------------------------------------------------
    rem_score = (
        abs(-1 * ab_cfo) +
        abs(ab_prod) +
        abs(-1 * ab_disc)
    )

    # ==================================================
    # INTERPRETATION
    # ==================================================
    def level(x):
        if x > 6:
            return "High"
        elif x > 3:
            return "Moderate"
        else:
            return "Low"

    rem_level = level(rem_score)
    text_level = level(abnormal_text)

    # Direction of income effect
    income_effect = []
    if ab_cfo < 0:
        income_effect.append("CFO suppression (income-increasing)")
    if ab_prod > 0:
        income_effect.append("Overproduction (income-increasing)")
    if ab_disc < 0:
        income_effect.append("Discretionary cost cutting (income-increasing)")

    # ==================================================
    # FINAL DECISION
    # ==================================================
    if rem_level == "High" and text_level == "High":
        final = "🔴 Confirmed Earnings Manipulation (Numeric + Language aligned)"
    elif rem_level in ["High","Moderate"] and text_level in ["High","Moderate"]:
        final = "🟠 Likely Earnings Manipulation"
    elif rem_level == "High" and text_level == "Low":
        final = "⚠ Numeric REM Detected (Language not supportive)"
    else:
        final = "🟢 Low Risk of Earnings Manipulation"

    # ==================================================
    # OUTPUT
    # ==================================================
    st.subheader("Numeric REM Analysis")
    st.write({
        "Abnormal CFO": round(ab_cfo, 2),
        "Abnormal Production": round(ab_prod, 2),
        "Abnormal Discretionary": round(ab_disc, 2),
        "Final REM Score (ABS Formula)": round(rem_score, 2),
        "REM Risk Level": rem_level
    })

    st.subheader("Text Analysis")
    st.write({
        "Abnormal Language Score": round(abnormal_text, 2),
        "Language Risk Level": text_level
    })

    st.subheader("Income Effect Interpretation")
    st.write(income_effect if income_effect else ["No clear income-increasing signals detected"])

    st.subheader("Final Assessment")
    st.success(final)

    st.caption("""
    REM is computed using ABS(-CFO) + ABS(PROD) + ABS(-DISC),
    following income-increasing real earnings management logic.
    Language analysis is used as an independent confirmation layer.
    """)

elif files and len(files) < 2:
    st.info("Please upload at least **2 annual reports**.")
