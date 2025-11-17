import streamlit as st
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="Cashflow Timeline", layout="wide")

st.title("📈 Cashflow Timeline Manager")

# ---------------------------------------------------
# Load file (CSV or JSON)
# ---------------------------------------------------
def load_file(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame(columns=["Date", "Description", "Amount"])
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith(".json"):
        raw = json.load(uploaded_file)
        df = pd.DataFrame(raw)
    else:
        st.error("File must be CSV or JSON")
        return pd.DataFrame(columns=["Date", "Description", "Amount"])

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

    return df


uploaded = st.file_uploader("📥 Load CSV or JSON file", type=["csv", "json"])

df = load_file(uploaded)

st.subheader("✏️ Edit Entries")

# ---------------------------------------------------
# Editable table
# ---------------------------------------------------
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True
)

# ---------------------------------------------------
# Compute timeline + cumulative
# ---------------------------------------------------
st.subheader("📊 Timeline and Cashflow Summary")

if not edited_df.empty:
    tmp = edited_df.copy()
    tmp["Date"] = pd.to_datetime(tmp["Date"])
    tmp = tmp.sort_values("Date")
    tmp["Cumulative"] = tmp["Amount"].cumsum()

    st.line_chart(tmp.set_index("Date")["Cumulative"])
    st.write(tmp)
else:
    st.info("Add entries above to generate a timeline.")

# ---------------------------------------------------
# Save buttons
# ---------------------------------------------------
st.subheader("💾 Export Data")

col1, col2 = st.columns(2)

with col1:
    csv_data = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download as CSV",
        data=csv_data,
        file_name="cashflow.csv",
        mime="text/csv"
    )

with col2:
    json_data = edited_df.to_json(orient="records", indent=2)
    st.download_button(
        label="Download as JSON",
        data=json_data,
        file_name="cashflow.json",
        mime="application/json"
    )
