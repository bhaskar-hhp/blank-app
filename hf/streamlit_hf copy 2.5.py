import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("/home/swiftcomcdpl/key/firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------------------
# 🔐 LOGIN SECTION
# -------------------------------

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users_ref = db.collection("users")
        query = users_ref.where("name", "==", username).where("pass", "==", password).get()
        if query:
            user_data = query[0].to_dict()
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = user_data.get("type", "Standard")
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials")


# -------------------------------
# 🚪 LOGOUT FUNCTION
# -------------------------------
def logout():
    for key in ["logged_in", "username", "user_role", "selected_page"]:
        st.session_state.pop(key, None)
    st.success("Logged out successfully.")
    st.rerun()



# Inject custom CSS
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 45px;
        font-size: 16px;
        margin-bottom: 8px;
        background-color: #31333f;
        color: white;
        border: none;
        border-radius: 6px;
    }

    div.stButton > button:hover {
        background-color: #505266;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧭 SIDEBAR NAVIGATION
# -------------------------------
def show_sidebar():
    user_role = st.session_state.get("user_role")
    with st.sidebar:
        st.title("📂 Navigation")

        # Common for all roles
        if st.button("🏠 Home"):
            st.session_state.selected_page = "Home"

        # Admin only
        if user_role == "Admin":
            if st.button("📝 Users"):
                st.session_state.selected_page = "Users"
            if st.button("📊 Distributors"):
                st.session_state.selected_page = "Distributors"

        if st.button("🚪 Logout"):
            logout()


# -------------------------------
# 🌐 PAGE CONTENT
# -------------------------------
def home_page():
    st.title("🏠 Home Page")
    st.write("Welcome to the homepage.")

def users_page():
    if st.session_state.get("user_role") != "Admin":
        st.error("Access denied.")
        return
    st.title("📝 User Management")
    st.write("You can add, update, or delete users here.")

def distributors_page():
    if st.session_state.get("user_role") != "Admin":
        st.error("Access denied.")
        return
    st.title("📊 Distributor Management")
    st.write("You can manage distributors here.")


# -------------------------------
# 🚀 MAIN APP
# -------------------------------
def main():
    if not st.session_state.get("logged_in"):
        login()
        return

    show_sidebar()

    page = st.session_state.get("selected_page", "Home")
    if page == "Home":
        home_page()
    elif page == "Users":
        users_page()
    elif page == "Distributors":
        distributors_page()

main()
