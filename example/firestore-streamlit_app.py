import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection("users")

st.title("📋 Firestore User Manager")

# Fetch users from Firestore
def fetch_users():
    docs = users_ref.stream()
    return [doc.to_dict() for doc in docs]

# Get users
users = fetch_users()
df = pd.DataFrame(users)

# Show user table
if not df.empty:
    st.subheader("📄 Users Table")
    st.dataframe(df)
else:
    st.info("No users in the database.")

# --- ADD USER ---
st.subheader("➕ Add New User")
with st.form("add_user_form"):
    uid = st.text_input("User ID (e.g., u005)")
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["Admin", "User", "Guest"])
    location = st.text_input("Location")
    add_submitted = st.form_submit_button("Add User")

    if add_submitted:
        if uid and name and email:
            users_ref.document(uid).set({
                "id": uid,
                "name": name,
                "email": email,
                "role": role,
                "location": location
            })
            st.success(f"User '{name}' added!")
            st.rerun()
        else:
            st.error("Please fill in all required fields.")

# --- DELETE USER ---
st.subheader("🗑️ Delete User")
user_ids = df["id"].tolist() if not df.empty else []
selected_delete = st.selectbox("Select User ID to Delete", user_ids)
if st.button("Delete User"):
    if selected_delete:
        users_ref.document(selected_delete).delete()
        st.warning(f"User '{selected_delete}' deleted.")
        st.rerun()

# --- EDIT/UPDATE USER ---
st.subheader("✏️ Edit User")
selected_edit = st.selectbox("Select User ID to Edit", user_ids, key="edit_select")
if selected_edit:
    user_doc = users_ref.document(selected_edit).get().to_dict()
    if user_doc:
        with st.form("edit_user_form"):
            name_edit = st.text_input("Name", user_doc.get("name", ""))
            email_edit = st.text_input("Email", user_doc.get("email", ""))
            role_edit = st.selectbox("Role", ["Admin", "User", "Guest"], index=["Admin", "User", "Guest"].index(user_doc.get("role", "User")))
            location_edit = st.text_input("Location", user_doc.get("location", ""))
            update_submitted = st.form_submit_button("Update User")

            if update_submitted:
                users_ref.document(selected_edit).update({
                    "name": name_edit,
                    "email": email_edit,
                    "role": role_edit,
                    "location": location_edit
                })
                st.success(f"User '{selected_edit}' updated.")
                st.rerun()
