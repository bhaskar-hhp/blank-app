import streamlit as st
import sqlite3

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

# --- Connect to DB ---
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

st.title("Add New User")
with st.form("add_form"):
    name = st.text_input("Enter User Name: ").strip().upper()
    user_type = st.selectbox("User Type", ["Admin", "Standard", "Guest"])
    password = st.text_input("Create Password", type="password")
    submit = st.form_submit_button("Add")

    if submit:
        if not name or not password:
            st.warning("Please provide both a name and a password.")
        else:
            cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)", (name, user_type, password))
            conn.commit()
            st.success(f"User '{name}' added!")
            st.rerun()

st.markdown("---")

with open("add-bulk.csv", "rb") as f:
    st.download_button(
        label="📅 Download CSV Format",

        data=f,
        file_name="add-bulk.csv",
        mime="text/csv"
    )

st.subheader("📂 Upload CSV to Add Users in Bulk")
csv_file = st.file_uploader("Upload a CSV file with columns: name, type, pass", type="csv")

if csv_file and "processed_bulk_upload" not in st.session_state:
    import pandas as pd
    try:
        df = pd.read_csv(csv_file)
        required_cols = {"name", "type", "pass"}
        if not required_cols.issubset(df.columns.str.lower()):
            st.error(f"CSV must include the following columns: {', '.join(required_cols)}")
        else:
            df.columns = df.columns.str.lower()
            df["name"] = df["name"].str.strip().str.upper()
            for _, row in df.iterrows():
                cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)",
                               (row["name"], row["type"], row["pass"]))
            conn.commit()
            st.success(f"{len(df)} users added successfully!")
            st.session_state.processed_bulk_upload = True
    except Exception as e:
        st.error(f"Error processing file: {e}")

conn.close()
