import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="User Manager App",  # This sets the browser tab title
    page_icon="/workspaces/blank-app/BJ LOGO 2.jpg",               # Optional: sets a favicon (emoji or URL)
    layout="centered"              # Optional: wide, centered, etc.
)
st.title("👋 Welcome to the User Manager App")

# --- Connect to DB ---
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# --- Update users table schema ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    pass TEXT
)
""")
conn.commit()

# --- Persistent sidebar using session_state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Form at Startup
if not st.session_state.logged_in:
    st.subheader("Please Login")
    
    # Login form
    with st.form("login_form"):
        name = st.text_input("Enter User Name: ")
        password = st.text_input("Enter Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Check if user exists in DB and password matches
            cursor.execute("SELECT * FROM users WHERE name = ? AND pass = ?", (name, password))
            user = cursor.fetchone()
            
            if user:
                # Store user type in session_state
                st.session_state.logged_in = True
                st.session_state.user_type = user[2]  # User type is in 3rd column (index 2)
                st.success(f"Welcome {name}! You are logged in as {user[2]}.")
                st.rerun()  # Refresh the page to show the correct page
            else:
                st.error("Invalid credentials, please try again.")

# --- Sidebar navigation ---
if st.session_state.logged_in:
    st.sidebar.image("/workspaces/blank-app/BJ LOGO 2.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    
    # Role-based page navigation
    if st.session_state.user_type == "Admin":
        st.session_state.page = st.sidebar.radio("Choose page", ["View Users", "Add User", "Delete User"])
    elif st.session_state.user_type in ["Standard", "Guest"]:
        st.session_state.page = st.sidebar.radio("Choose page", ["View Users"])

    # --- Page: Add User ---
    if st.session_state.page == "Add User" and st.session_state.user_type == "Admin":
        st.title("Add New User")
        with st.form("add_form"):
            name = st.text_input("Enter User Name: ")
            user_type = st.selectbox("User Type", ["Admin", "Standard", "Guest"])
            password = st.text_input("Create Password", type="password")

            st.title("All Users")
            df = pd.read_sql_query("SELECT * FROM users", conn)
            st.dataframe(df, use_container_width=True)

            submit = st.form_submit_button("Add")
            if submit:
                # Validation to ensure no empty fields
                if not name or not password:
                    st.warning("Please provide both a name and a password.")
                else:
                    cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)", (name, user_type, password))
                    conn.commit()
                    st.success(f"User '{name}' added!")
                    st.rerun()  # Refresh the page after adding user

    # --- Page: View Users ---
    elif st.session_state.page == "View Users":
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)

    # --- Page: Delete User ---
    if st.session_state.page == "Delete User" and st.session_state.user_type == "Admin":
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
                st.rerun()  # Refresh the page after deletion

# --- Close the connection when the app ends ---
conn.close()
