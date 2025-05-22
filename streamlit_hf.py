import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import io
from datetime import datetime


# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
st.Page.title="Swiftcom DMS"
st.set_page_config(layout="wide")
# -------------------------------
# 🔐 LOGIN SECTION
# -------------------------------
def login():
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username").strip().upper()
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
        background-color: #125078;
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
        st.markdown(f"**👤 {st.session_state.get('username')} (:blue[{user_role}])**")
        st.title("📂 Navigation")

        # All roles: Home
        if st.button("🏠 Home"):
            st.session_state.selected_page = "Home"

        if st.button("🕒 Attendance"):
            st.session_state.selected_page = "Attendance"

        # Admin , "Standard", "Guest": -----------------------------------------------------------------------------
        if user_role in ["Admin", "Standard", "Guest"]:
            if st.button("📦Purchase Order"):
                st.session_state.selected_page = "Order"

        # Admin , Back Office: -----------------------------------------------------------------------------
        if user_role in ["Admin", "Back Office"]:
            if st.button("📦 Update Order"):
                st.session_state.selected_page = "Update Order"
            if st.button("📱 Devices"):
                st.session_state.selected_page = "Devices"
            if st.button("📊 Distributors"):
                st.session_state.selected_page = "Distributors"
            if st.button("🚚 Logistics"):
                st.session_state.selected_page = "Logistics"

        # Admin Only --------------------------------------------------------------------------------------
        if user_role in ["Admin"]:
            if st.button("📝 Users"):
                st.session_state.selected_page = "Users"
            if st.button("🛠️ Utility"):
                st.session_state.selected_page = "Utility"
            if st.button("🕒 Attendance Managment"):
                st.session_state.selected_page = "Attendance Managment"

        # --------------------------------------------------------------------------------------------------


        if st.button("ℹ️ About"):
            st.session_state.selected_page = "About"

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

    #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            📝 User Management
        </h5>
        """,
        unsafe_allow_html=True
    )
    #----------------------------------------------------------------

    # Choose form actions
    options = ["View User"]
    if user_role in ["Admin", "Back Office"]:
        options.append("Add User")
    if user_role == "Admin":
        options.extend(["Delete User", "Update User"])
        #st.divider()
        user_option = st.radio("Choose action", options, horizontal=True)
        st.divider()

    # Add User
    if user_option == "Add User":
        st.subheader("Add New User")
        with st.form("add_user_form"):
            name = st.text_input("Name").strip().upper()
            user_type = st.selectbox("Type", ["Admin", "Back Office","Standard", "Guest"])
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
                df = pd.DataFrame(user_data)
                column_order = ["name", "pass", "type"]  # Rearrange as needed
                ordered_columns = [col for col in column_order if col in df.columns] + [col for col in df.columns if col not in column_order and col != "doc_id"]
                st.dataframe(df[ordered_columns])
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

# -----------------------------------------Distributors placeholder

def distributors_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        return
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            📊 Distributor Management
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    COLLECTION = "Dist"

    # Firebase operations
    def add_distributor(data):
        db.collection(COLLECTION).add(data)

    def get_distributors():
        docs = db.collection(COLLECTION).stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    def update_distributor(doc_id, data):
        db.collection(COLLECTION).document(doc_id).update(data)

    def delete_distributor(doc_id):
        db.collection(COLLECTION).document(doc_id).delete()

    # Streamlit UI
    
    option = st.radio("Select Operation", ["View", "Add", "Bulk Add", "Update", "Delete"],horizontal=True)
    st.divider()

    if option == "View":
        st.subheader("View Distributors")
        records = get_distributors()
        if records:   
            # Specify the desired column order
            df = pd.DataFrame(records)
            column_order = ["name", "location","address", "contact", "email"]  # Rearrange as needed
            ordered_columns = [col for col in column_order if col in df.columns] + [col for col in df.columns if col not in column_order and col != "id"]
            st.dataframe(df[ordered_columns])
        else:
            st.info("No distributors found.")

    elif option == "Add":
        st.subheader("Add Distributor")
        

        records = get_distributors()
        df1 = pd.DataFrame(records)
        loc = st.selectbox("Location", df1["location"]).strip().upper()
        st.write("if location not in the list, prefer add in location Textbox")
        st.divider()
        name = st.text_input("Name").strip().upper()

        if st.checkbox("Add New Loaction"):
            location = st.text_input("Location").strip().upper()
        else:
            location = loc

        address = st.text_area("Address (multiline)")
        contact = st.text_input("Contact")
        email = st.text_input("Email")
        if st.button("Add"):
            if name:
                add_distributor({"name": name, "location": location,"address": address, "contact": contact, "email": email})
                st.success("Distributor added.")
            else:
                st.warning("Name is required.")

    elif option == "Bulk Add":
        st.subheader("Bulk Add Distributors (CSV)")
        st.markdown("CSV columns: name, location, address, contact, email")
        # Download CSV template
        template_df = pd.DataFrame(columns=["name", "location", "address", "contact", "email"])
        csv = template_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV Template", csv, "distributor_template.csv", "text/csv")

        # Upload CSV
        file = st.file_uploader("Upload CSV", type="csv")
        if file:
            df = pd.read_csv(file)
            if all(col in df.columns for col in ["name", "location", "address", "contact", "email"]):
                for _, row in df.iterrows():
                    add_distributor(row.to_dict())
                st.success("Bulk upload complete.")
            else:
                st.error("CSV must have columns: name, location, address, contact, email")

    elif option == "Update":
        st.subheader("Update Distributor")
        records = get_distributors()
        if records:
            df = pd.DataFrame(records)
            selected = st.selectbox("Select Distributor by Name", df["name"])
            selected_data = df[df["name"] == selected].iloc[0]
            st.divider()
            doc_id = selected_data["id"]
            name = st.text_input("Name", selected_data["name"]).strip().upper()
            location = st.text_input("Location", selected_data["location"]).strip().upper()
            address = st.text_area("Address", selected_data["address"])
            contact = st.text_input("Contact", selected_data["contact"])
            email = st.text_input("Email", selected_data["email"])
            if st.button("Update"):
                update_distributor(doc_id, {"name": name, "location": location,"address": address, "contact": contact, "email": email})
                st.success("Distributor updated.")
        else:
            st.info("No distributors available.")

    elif option == "Delete":
        st.subheader("Delete Distributor")
        records = get_distributors()
        if records:
            df = pd.DataFrame(records)
            selected = st.selectbox("Select Distributor to Delete", df["name"])
            doc_id = df[df["name"] == selected]["id"].values[0]
            if st.button("Delete"):
                delete_distributor(doc_id)
                st.success("Distributor deleted.")
        else:
            st.info("No distributors to delete.")

# ---------------------------------------------------------------Order Page----------------------
def order_page():
    if st.session_state.get("user_role") not in ["Admin", "Standard", "Guest"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            📦 Order Management
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------




# ---------------------------------------------------------------Order Page----------------------
def devices_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            📱 Devices
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------
    




# ---------------------------------------------------------------Logistics Page----------------------
def logistics_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")

    #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            🚚 Logistics
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

# ---------------------------------------------------------------Utility Page----------------------
def utility_page():
    if st.session_state.get("user_role") not in ["Admin"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            🛠️ Utility
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------
    

# ---------------------------------------------------------------Attendance Page----------------------
def attendance_page():
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            🕒 Attendance
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    st.write("Attendance Page comming soon")



# ---------------------------------------------------------------About Page----------------------
def about_page():
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            ℹ️ About
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    st.write("About page is comming soon")


# ---------------------------------------------------------------Update Order Page----------------------
def update_order_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            📦 Update Order
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    st.write("Update Order page is comming soon")



# ---------------------------------------------------------------Attendance Managment Page----------------------
def att_managment_page():
    if st.session_state.get("user_role") not in ["Admin"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='background-color:#125078; padding:10px; border-radius:10px; color:white;'>
            🕒 Attendance Managment
        </h5>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    st.write("Attendance Managment page is comming soon")


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
    elif page == "Order":
        order_page()
    elif page == "Logistics":
        logistics_page()
    elif page == "Utility":
        utility_page()
    elif page == "Attendance":
        attendance_page()
    elif page == "About":
        about_page()
    elif page == "Update Order":
        update_order_page()
    elif page == "Attendance Managment":
        att_managment_page()
    elif page == "Devices":
        devices_page()



if __name__ == "__main__":
    main()
