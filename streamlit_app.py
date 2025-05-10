import streamlit as st

st.set_page_config(page_title="Model Manager", page_icon="🛠️")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Very basic check; replace with proper authentication logic
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials.")
else:
    st.title("Welcome to Model Manager!")
    st.sidebar.success("Use the sidebar to navigate.")