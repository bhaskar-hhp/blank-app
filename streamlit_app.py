import streamlit as st
import sqlite3
import pandas as pd

# Connect to DB
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
)
""")
conn.commit()

# --- Persistent sidebar using session_state ---
if "page" not in st.session_state:
    st.session_state.page = "Add User"

# Sidebar nav
st.sidebar.title("Navigation")
st.session_state.page = st.sidebar.radio("Choose page", ["View Users", "Add User", "Delete User"])

# --- Page: Add User ---
if st.session_state.page == "Add User":
    st.title("Add New User")
    with st.form("add_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)
        submit = st.form_submit_button("Add")
        if submit:
            cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
            conn.commit()
            st.success(f"User '{name}' added!")

# --- Page: View Users ---
elif st.session_state.page == "View Users":
    st.title("All Users")
    df = pd.read_sql_query("SELECT * FROM users", conn)
    st.dataframe(df, use_container_width=True)

# --- Page: Delete User ---
elif st.session_state.page == "Delete User":
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
            st.experimental_rerun()  # Refresh while keeping sidebar working
