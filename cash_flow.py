import streamlit as st
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="ניהול תזרים", layout="wide")

st.title("💰 ניהול תזרים מזומנים")

# ---------------------------------------------------
# טעינת קובץ
# ---------------------------------------------------
def load_file(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame(columns=["תאריך", "תיאור", "סוג", "סכום"])
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith(".json"):
        raw = json.load(uploaded_file)
        df = pd.DataFrame(raw)
    else:
        st.error("הקובץ חייב להיות CSV או JSON")
        return pd.DataFrame(columns=["תאריך", "תיאור", "סוג", "סכום"])

    if "תאריך" in df.columns:
        df["תאריך"] = pd.to_datetime(df["תאריך"]).dt.date

    return df


uploaded = st.file_uploader("📥 טען קובץ CSV או JSON", type=["csv", "json"])

df = load_file(uploaded)

st.subheader("✏️ עריכת תנועות תזרים")

# ---------------------------------------------------
# עורך הטבלה
# ---------------------------------------------------
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "סוג": st.column_config.SelectboxColumn(
            "סוג",
            help="בחר הכנסה או הוצאה",
            options=["הכנסה", "הוצאה"]
        )
    }
)

# ---------------------------------------------------
# עיבוד תזרים לפי סוג
# ---------------------------------------------------
if not edited_df.empty:
    df2 = edited_df.copy()
    df2["תאריך"] = pd.to_datetime(df2["תאריך"])
    
    # המרה של הסכום למספר, ריק = 0
    df2["סכום"] = pd.to_numeric(df2["סכום"], errors="coerce").fillna(0)
    
    # הפיכת הוצאה לשלילית
    def fix_amount(row):
        amount = row["סכום"]
        if row["סוג"] == "הכנסה":
            return amount
        else:
            return -abs(amount)
    
    df2["סכום_מתוקן"] = df2.apply(fix_amount, axis=1)


    st.subheader("📊 גרף תזרים לפי זמן")
    st.line_chart(df2.set_index("תאריך")["מצטבר"])

    st.write("📄 טבלה מלאה:")
    st.write(df2[["תאריך", "תיאור", "סוג", "סכום", "מצטבר"]])
else:
    st.info("הוסף תנועות כדי לראות גרף תזרים.")

# ---------------------------------------------------
# שמירה
# ---------------------------------------------------
st.subheader("💾 שמירת נתונים")

col1, col2 = st.columns(2)

with col1:
    csv_data = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📤 הורדה כ-CSV",
        data=csv_data,
        file_name="cashflow.csv",
        mime="text/csv"
    )

with col2:
    json_data = edited_df.to_json(orient="records", indent=2, force_ascii=False)
    st.download_button(
        label="📤 הורדה כ-JSON",
        data=json_data,
        file_name="cashflow.json",
        mime="application/json"
    )
