import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Delete User", page_icon="🗑️", layout="centered")

conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

st.title("Delete a User")
df = pd.read_sql_query("SELECT * FROM users", conn)

if df.empty:
    st.info("No users found.")
else:
    st.dataframe(df)
    selected_id = st.radio("Select User ID to Delete", df["id"])
    selected_user = df[df["id"] == selected_id]
    st.write("Selected User:")
    st.table(selected_user)

    if st.button("Delete"):
        cursor.execute("DELETE FROM users WHERE id = ?", (selected_id,))
        conn.commit()
        st.success(f"User with ID {selected_id} deleted.")
        st.rerun()

# Reset Users Table
confirm_reset = st.checkbox("Are you sure you want to delete all Users?")
if st.button("Reset All Users Data"):
    if confirm_reset:
        cursor.execute("DELETE FROM users")
        conn.commit()
        st.success("All users have been deleted.")
        st.rerun()
    else:
        st.info("Please check the box to confirm before resetting the Users.", icon="⚠️")

conn.close()
