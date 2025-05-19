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
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
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
    for key in ["logged_in", "username", "user_role", "selected_page", "user_option", "dist_option"]:
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
        st.markdown(f"**👤 {st.session_state.get('username')} ({user_role})**")
        st.title("📂 Navigation")

        # All roles: Home
        if st.button("🏠 Home"):
            st.session_state.selected_page = "Home"

        # Admin & Standard: Users
        if user_role in ["Admin", "Standard"]:
            if st.button("📝 Users"):
                st.session_state.selected_page = "Users"

        # Admin only: Distributors
        if user_role == "Admin":
            if st.button("📊 Distributors"):
                st.session_state.selected_page = "Distributors"

        # Logout button
        if st.button("🚪 Logout"):
            logout()

# -------------------------------
# 🌐 PAGE CONTENT
# -------------------------------
def home_page():
    st.title("🏠 Home Page")
    st.write("Welcome to the homepage.")

# Users Management with radio options

def users_page():
    user_role = st.session_state.get("user_role")
    if user_role not in ["Admin", "Standard"]:
        st.error("Access denied.")
        return

    st.title("📝 User Management")
    # Choose form actions
    options = ["View User"]
    if user_role in ["Admin", "Standard"]:
        options.append("Add User")
    if user_role == "Admin":
        options.extend(["Delete User", "Update User"])

    user_option = st.radio("Choose action", options, horizontal=True)

    # Add User
    if user_option == "Add User":
        st.subheader("Add New User")
        with st.form("add_user_form"):
            name = st.text_input("Name")
            user_type = st.selectbox("Type", ["Admin", "Standard", "Guest"])
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Submit")
        if submitted:
            users_ref = db.collection("users")
            all_users = users_ref.stream()
            max_id = 0
            for doc in all_users:
                data = doc.to_dict()
                if isinstance(data.get("id"), int):
                    max_id = max(max_id, data["id"])
            new_id = max_id + 1
            users_ref.add({"id": new_id, "name": name, "type": user_type, "pass": password})
            st.success(f"✅ User '{name}' added with ID {new_id}.")

    # View User
    elif user_option == "View User":
        st.subheader("📋 List of Users")
        try:
            docs = db.collection("users").get()
            user_data = [{**doc.to_dict(), "doc_id": doc.id} for doc in docs]
            if user_data:
                st.dataframe(user_data)
            else:
                st.info("No users found.")
        except Exception as e:
            st.error(f"Error fetching users: {e}")

    # Delete User (Admin only)
    elif user_option == "Delete User":
        st.subheader("🗑️ Delete User")
        docs = db.collection("users").get()
        usernames = [doc.to_dict().get("name") for doc in docs]
        to_delete = st.selectbox("Select user to delete", usernames)
        if st.button("Delete"):
            # find doc
            for doc in docs:
                if doc.to_dict().get("name") == to_delete:
                    db.collection("users").document(doc.id).delete()
                    st.success(f"Deleted user {to_delete}.")
                    break

    # Update User (Admin only)
    elif user_option == "Update User":
        st.subheader("✏️ Update User")
        docs = db.collection("users").get()
        usernames = [doc.to_dict().get("name") for doc in docs]
        to_update = st.selectbox("Select user to update", usernames)
        new_type = st.selectbox("New Type", ["Admin", "Standard", "Guest"])
        new_pass = st.text_input("New Password", type="password")
        if st.button("Update"):
            for doc in docs:
                if doc.to_dict().get("name") == to_update:
                    update_data = {}
                    if new_type:
                        update_data["type"] = new_type
                    if new_pass:
                        update_data["pass"] = new_pass
                    db.collection("users").document(doc.id).update(update_data)
                    st.success(f"Updated user {to_update}.")
                    break

# Distributors placeholder

def distributors_page():
    if st.session_state.get("user_role") != "Admin":
        st.error("Access denied.")
        return
    st.title("📊 Distributor Management")
    st.write("Manage distributors here.")

# -------------------------------
# 🚀 MAIN APP
# -------------------------------
def main():
    if not st.session_state.get("logged_in"):
        login()
        return

    # set default page
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    show_sidebar()

    page = st.session_state.selected_page
    if page == "Home":
        home_page()
    elif page == "Users":
        users_page()
    elif page == "Distributors":
        distributors_page()

if __name__ == "__main__":
    main()
