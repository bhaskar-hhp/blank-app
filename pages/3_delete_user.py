import streamlit as st
import sqlite3
import pandas as pd

st.title("🗑️ Delete a User")

# Connect to the renamed database
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# Load users table
df = pd.read_sql_query("SELECT * FROM users", conn)

if df.empty:
    st.info("No users found.")
else:
    st.dataframe(df, use_container_width=True)

    selected_id = st.radio("Select User ID to Delete", df["id"])
    selected_row = df[df["id"] == selected_id]

    st.subheader("Selected User:")
    st.table(selected_row)

    if st.button("Delete"):
        cursor.execute("DELETE FROM users WHERE id = ?", (selected_id,))
        conn.commit()
        st.success(f"✅ User with ID {selected_id} deleted.")
        st.rerun()  # Refresh the page
