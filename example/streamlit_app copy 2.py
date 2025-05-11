import streamlit as st
import sqlite3

st.set_page_config(page_title="Model Manager", page_icon="🛠️")

# Connect to DB
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "usertype" not in st.session_state:
    st.session_state.usertype = ""

# Login logic
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute("SELECT * FROM users WHERE name = ? AND pass = ?", (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.usertype = user[2]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")
else:
    # Sidebar shown only after login
    st.sidebar.title("Navigation")
    st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.usertype})")

    st.title("🏠 Home")
    st.write("Welcome to the Model Manager dashboard.")

    # Optional: logout button
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "username", "usertype"]:
            st.session_state.pop(key, None)
        st.rerun()
