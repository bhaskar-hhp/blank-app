import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


# Initialize Firestore only once
# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("/home/swiftcomcdpl/key/firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize page
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

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

# Sidebar buttons
with st.sidebar:
    st.title("📂 Navigation")

    if st.button("🏠 Home"):
        st.session_state.selected_page = "Home"
    if st.button("📝 User Form"):
        st.session_state.selected_page = "User Form"
    if st.button("📊 Distributors"):
        st.session_state.selected_page = "Distributors"

    # USER Form radio options
    if st.session_state.selected_page == "User Form":
        user_option = st.radio(
            "Choose form",
            ("View User", "Add User", "Delete User", "Update User")
        )
        st.session_state.user_option = user_option

    # DISTRIBUTORS radio options
    if st.session_state.selected_page == "Distributors":
        dist_option = st.radio(
            "Choose form",
            ("View Distributor", "Add Distributor", "Delete Distributor", "Update Distributor")
        )
        st.session_state.dist_option = dist_option

# Render selected page
page = st.session_state.selected_page

if page == "Home":
    st.title("🏠 Home Page")
    st.write("Welcome to the homepage.")

elif page == "User Form":
    st.title("📝 User Form Page")

    # Handle Add User
    if st.session_state.get("user_option") == "Add User":
        st.subheader("Add New User")

        with st.form("add_user_form"):
            name = st.text_input("Name")
            user_type = st.selectbox("Type", ["Admin", "Standard", "Guest"])
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Submit")

        if submitted:
            # Get current max ID
            users_ref = db.collection("users")
            all_users = users_ref.stream()
            max_id = 0
            for doc in all_users:
                doc_data = doc.to_dict()
                if "id" in doc_data and isinstance(doc_data["id"], int):
                    max_id = max(max_id, doc_data["id"])

            new_id = max_id + 1

            # Save to Firestore
            users_ref.add({
                "id": new_id,
                "name": name,
                "type": user_type,
                "pass": password
            })

            st.success(f"✅ User '{name}' added with ID {new_id}.")

    if st.session_state.get("user_option") == "View User":
        st.subheader("📋 List of Users")

        try:
            users_ref = db.collection("users")
            docs = db.collection("users").get()

            user_data = []
            for doc in docs:
                user = doc.to_dict()
                user["doc_id"] = doc.id
                user_data.append(user)

            if user_data:
                st.dataframe(user_data)
            else:
                st.info("No users found.")
        except Exception as e:
            st.error(f"Error fetching users: {e}")

elif page == "Distributors":
    st.title("📊 Distributors Page")
    st.write("Reports section coming soon.")
