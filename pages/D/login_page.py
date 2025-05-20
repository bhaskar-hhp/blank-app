import streamlit as st


def show_login():
    st.title("🔐 Login Page")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

    return st.session_state.authenticated
