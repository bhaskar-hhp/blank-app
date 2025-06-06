import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import io
from io import StringIO
from datetime import datetime
import time
import uuid
from PIL import Image
import os
import base64

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
@st.dialog("🔐 Login")
def login():
    
    #st.title("🔐 Login")
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


        # Admin , "Standard", "Back Office": -----------------------------------------------------------------------------
        if user_role in ["Admin", "Standard", "Back Office"]:
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
            if st.button("📊 Distributors Ledgers"):
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

        # Guest Only --------------------------------------------------------------------------------------
        if user_role in ["Guest"]:
            if st.button("📝 Ledger"):
                st.session_state.selected_page = "Ledger"
     
        # --------------------------------------------------------------------------------------------------

        # Standard Only --------------------------------------------------------------------------------------
        if user_role in ["Standard"]:
            if st.button("📝 Ledgers"):
                st.session_state.selected_page = "Ledgers"
     
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
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        with st.form("add_user_form"):
            #image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
            col1, col2 = st.columns([1,3],gap="small",border=True)
            with col1:
                # Image preview
                if image_file:
                    st.write("Image Uploaded:")
                    try:
                        image = Image.open(image_file)
                        
                        st.image(image, caption="Image Preview", width=150)                    
                    except Exception as e:
                        st.error(f"Error opening image: {e}")
                else:
                    st.write("Image not uploaded")    
            with col2:
                name = st.text_input("Name").strip().upper()
                user_type = st.selectbox("Type", ["Admin", "Back Office", "Standard", "Guest"])
                password = st.text_input("Password", type="password")

            with st.expander("Add additional user details"):
                col3, col4 = st.columns(2,gap="small",border=True)
                with col3:
                    full_name=st.text_input("Full Name").strip().upper()
                    doj_in=st.date_input("Date of Joining")
                    doj = doj_in.strftime("%d-%m-%Y")
                    dob_in=st.date_input("Date of Birth")
                    dob = dob_in.strftime("%d-%m-%Y")
                    status=st.selectbox("Status", ["Active", "Inactive"])
                    contact=st.text_input("Contact").strip().upper()
                    work_area=st.text_input("Work Area").strip().upper()
                    work_profile=st.text_input("Work Profile").strip().upper()
                    Brand=st.text_input("Brand").strip().upper()
                with col4:
                    fname=st.text_input("Father's Name").strip().upper()
                    address=st.text_area("Address").strip().upper()
                    email=st.text_input("Email").strip().upper()
                    doc_url=st.text_input("Document URL").strip()
                    Closing_Date_in=st.date_input("Closing Date")
                    Closing_Date=Closing_Date_in.strftime("%d-%m-%Y")


            # Submit button
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                users_ref = db.collection("users")
                all_users = users_ref.stream()
                
                # Check for duplicate user name
                name_exists = False
                max_id = 0
                for doc in all_users:
                    data = doc.to_dict()
                    if data.get("name") == name:
                        name_exists = True
                    if isinstance(data.get("id"), int):
                        max_id = max(max_id, data["id"])
                
                image_b64 = ""
                if image_file:
                    img = Image.open(image_file)
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    image_b64 = base64.b64encode(buffered.getvalue()).decode()


                if name_exists:
                    st.error(f"⚠️ User name '{name}' already exists. Please choose another name.")
                else:
                    new_id = max_id + 1
                    users_ref.add({"id": new_id,"image_b64":image_b64, "name": name, "type": user_type, "pass": password, "full_name":full_name, "doj":doj,"dob":dob,"status":status,"contact":contact,"work_area":work_area,"work_profile":work_profile,"Brand":Brand,"fname":fname,"address":address,"email":email,"doc_url":doc_url,"Closing_Date":Closing_Date})
                    st.success(f"✅ User '{name}' added with ID {new_id}.")

    # View User
    elif user_option == "View User":
        st.subheader("📋 View Users Database ")
        docs = db.collection("users").stream()
        all_users = [doc.to_dict() for doc in docs]
        brand_options = sorted(set(user.get("Brand", "N/A") for user in all_users if user.get("Brand")))
        selected_brands = st.multiselect("Select Brands to filter", brand_options, default=brand_options)
        selected_type=st.selectbox("Select Type to filter",["Admin", "Back Office", "Standard", "Guest"])

        # Create 3 tabs
        tab1, tab2, tab3 = st.tabs(["🟢 Active Users", "🔴 Inactive Users", "❔ No Status Users"])

        # Fetch all users once
        docs = db.collection("users").stream()
        all_users = [doc.to_dict() for doc in docs]

        # Display helper function
        def show_users(users_list):
            for data in users_list:
                with st.container():
                    st.markdown(
                        """
                        <div style="border: 1px solid #2196F3; border-radius: 5px; padding: 1px; margin-bottom: 10px;">
                        """,
                        unsafe_allow_html=True
                    )

                    cols = st.columns([1, 3])
                    with cols[0]:
                        if data.get("image_b64"):
                            img_bytes = base64.b64decode(data["image_b64"])
                            st.image(img_bytes, width=80)
                        else:
                            st.write("❌ No Image")
                        st.markdown(f"`{data.get('full_name', 'N/A')}`")
                    with cols[1]:
                        c1, c2=st.columns(2,gap="small",border=True)
                        with c1:
                            st.markdown(f"**👤 User Name:** {data.get('name', 'N/A')}")
                            st.markdown(f"**🧑‍💻 Type:** {data.get('type', 'N/A')}")
                            st.markdown(f"**📌 Status:** {data.get('status', '❌ Not Set')}")
                            st.markdown(f"**💼 Brand:** {data.get('Brand', 'N/A')}")
                        with c2:
                            st.markdown(f"**📅 Date of Joining:** {data.get('doj', 'N/A')}")
                            st.markdown(f"**📅 Date of Birth:** {data.get('dob', 'N/A')}")
                            st.markdown(f"**📞 Contact:** {data.get('contact', 'N/A')}")

                        with st.expander(" 📂 `View additional user details`"):
                            c3, c4=st.columns(2,gap="small",border=True)
                            with c3:
                                st.markdown(f"**💼 Work Area:** {data.get('work_area', 'N/A')}")
                                st.markdown(f"**💼 Work Profile:** {data.get('work_profile', 'N/A')}")
                                st.markdown(f"**📧 Email:** {data.get('email', 'N/A')}")
                                st.markdown(f"**📅 Closing Date:** {data.get('Closing_Date', 'N/A')}")
                            with c4:
                                st.markdown(f"**👤 Father Name:** {data.get('fname', 'N/A')}")
                                st.markdown(f"**🏠 Address:** {data.get('address', 'N/A')}")
                                
                                
                                #st.markdown(f"**📄 Document URL:** {data.get('doc_url', 'N/A')}")
                                doc_url = data.get("doc_url")
                                if doc_url:
                                    st.link_button("📄 Open Document", doc_url)
                                else:
                                    st.write("❌ No Document URL")


                    st.markdown("</div>", unsafe_allow_html=True)

        # 🟢 Active
        with tab1:
            active_users = [
                u for u in all_users 
                if u.get("status", "").lower() == "active" and u.get("Brand") in selected_brands and u.get("type") == selected_type
                ]
            if active_users:
                st.write(f"🎯 {len(active_users)} `active user(s) matched with selected brands.`")
                show_users(active_users)
            else:
                st.info("No active users found.")

        # 🔴 Inactive
        with tab2:
            inactive_users = [
                u for u in all_users 
                if u.get("status", "").lower() == "inactive" and u.get("Brand") in selected_brands and u.get("type") == selected_type
            ]
            if inactive_users:
                st.write(f"🎯 {len(inactive_users)} `inactive user(s) matched with selected brands.`")
                show_users(inactive_users)
            else:
                st.info("No inactive users found.")

        # ❔ No Status
        with tab3:
            no_status_users = [
                u for u in all_users 
                if not u.get("status") or not u.get("Brand")
            ]
            if no_status_users:
                st.write(f"🎯 {len(no_status_users)} ` user(s) found without STATUS or BRAND selected.`")
                show_users(no_status_users)
            else:
                st.info("All users have status set.")


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
        
        users_ref = db.collection("users")
        docs = users_ref.stream()
        user_list = []
        user_dict = {}
        for doc in docs:
            data = doc.to_dict()
            name = data.get("name", "")
            user_list.append(name)
            user_dict[name] = {"doc_id": doc.id, "data": data}

        selected_user = st.selectbox("Select User to Update", user_list)

        if selected_user:
            user_data = user_dict[selected_user]["data"]
            doc_id = user_dict[selected_user]["doc_id"]

            image_file = st.file_uploader("Upload New Image (optional)", type=["png", "jpg", "jpeg"])

            with st.form("update_user_form"):
                col1, col2 = st.columns([1, 3], gap="small", border=True)
                with col1:
                    if image_file:
                        st.write("New Image Uploaded:")
                        try:
                            image = Image.open(image_file)
                            st.image(image, caption="Preview", width=150)
                        except Exception as e:
                            st.error(f"Error opening image: {e}")
                    elif user_data.get("image_b64"):
                        st.image(base64.b64decode(user_data["image_b64"]), width=150)
                    else:
                        st.write("❌ No image available")

                with col2:
                    name = st.text_input("Name", value=user_data.get("name", "")).strip().upper()
                    user_type = st.selectbox("Type", ["Admin", "Back Office", "Standard", "Guest"], index=["Admin", "Back Office", "Standard", "Guest"].index(user_data.get("type", "Standard")))
                    password = st.text_input("Password", value=user_data.get("pass", ""), type="password")

                with st.expander("Update additional user details"):
                    col3, col4 = st.columns(2, gap="small", border=True)
                    with col3:
                        full_name = st.text_input("Full Name", value=user_data.get("full_name", "")).strip().upper()
                        #doj_in = st.date_input("Date of Joining", datetime.datetime.strptime(user_data.get("doj", "01-01-2000"), "%d-%m-%Y"))
                        #dob_in = st.date_input("Date of Birth", datetime.datetime.strptime(user_data.get("dob", "01-01-2000"), "%d-%m-%Y"))
                        status = st.selectbox("Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(user_data.get("status", "Active")))
                        contact = st.text_input("Contact", value=user_data.get("contact", "")).strip().upper()
                        work_area = st.text_input("Work Area", value=user_data.get("work_area", "")).strip().upper()
                        work_profile = st.text_input("Work Profile", value=user_data.get("work_profile", "")).strip().upper()
                        Brand = st.text_input("Brand", value=user_data.get("Brand", "")).strip().upper()
                    with col4:
                        fname = st.text_input("Father's Name", value=user_data.get("fname", "")).strip().upper()
                        address = st.text_area("Address", value=user_data.get("address", "")).strip().upper()
                        email = st.text_input("Email", value=user_data.get("email", "")).strip().upper()
                        doc_url = st.text_input("Document URL", value=user_data.get("doc_url", "")).strip()
                        Closing_Date_in = st.date_input("Closing Date", datetime.datetime.strptime(user_data.get("Closing_Date", "01-01-2099"), "%d-%m-%Y"))
                # Submit button
                submitted = st.form_submit_button("Update User")
                if submitted:
                    image_b64 = user_data.get("image_b64", "")
                    if image_file:
                        img = Image.open(image_file)
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        image_b64 = base64.b64encode(buffered.getvalue()).decode()

                    updated_data = {
                        "name": name,
                        "type": user_type,
                        "pass": password,
                        "image_b64": image_b64,
                        "full_name": full_name,
                        "doj": doj_in.strftime("%d-%m-%Y"),
                        "dob": dob_in.strftime("%d-%m-%Y"),
                        "status": status,
                        "contact": contact,
                        "work_area": work_area,
                        "work_profile": work_profile,
                        "Brand": Brand,
                        "fname": fname,
                        "address": address,
                        "email": email,
                        "doc_url": doc_url,
                        "Closing_Date": Closing_Date_in.strftime("%d-%m-%Y")
                    }

                    users_ref.document(doc_id).update(updated_data)
                    st.success(f"✅ User '{name}' updated successfully.")
                    
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
            column_order = ["name", "location","address", "contact", "email", "company"]  # Rearrange as needed
            ordered_columns = [col for col in column_order if col in df.columns] + [col for col in df.columns if col not in column_order and col != "id"]
            st.dataframe(df[ordered_columns])
        else:
            st.info("No distributors found.")

    elif option == "Add":
        st.subheader("Add Distributor")
        

        records = get_distributors()
        df1 = pd.DataFrame(records)
        loc = st.selectbox("Location", df1["location"]).strip().upper()
        st.write("if location not in the list, prefer add new location Checkbox[]")

        if st.checkbox("Add New Loaction"):
            location = st.text_input("Location").strip().upper()
        else:
            location = loc

        st.divider()
        name = st.text_input("Name")
        address = st.text_area("Address (multiline)")
        contact = st.text_input("Contact")
        email = st.text_input("Email")
        company = st.selectbox("Company", ["SWIFTCOM", "SHREE AGENCY"])


        st.divider()

        if st.button("Add"):
            if name:
                add_distributor({"name": name, "location": location,"address": address, "contact": contact, "email": email, "company": company})
                st.success("Distributor added.")
            else:
                st.warning("Name is required.")

    elif option == "Bulk Add":
        st.subheader("Bulk Add Distributors (CSV)")
        st.markdown("CSV columns: name, location, address, contact, email, company")
        # Download CSV template
        template_df = pd.DataFrame(columns=["name", "location", "address", "contact", "email", "company"])
        csv = template_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV Template", csv, "distributor_template.csv", "text/csv")

        # Upload CSV
        file = st.file_uploader("Upload CSV", type="csv")
        if file:
            df = pd.read_csv(file)
            if all(col in df.columns for col in ["name", "location", "address", "contact", "email", "company"]):
                for _, row in df.iterrows():
                    add_distributor(row.to_dict())
                st.success("Bulk upload complete.")
            else:
                st.error("CSV must have columns: name, location, address, contact, email, company")

    elif option == "Update":
        st.subheader("Update Distributor")
        records = get_distributors()
        if records:
            df = pd.DataFrame(records)
            selected = st.selectbox("Select Distributor by Name", df["name"])
            selected_data = df[df["name"] == selected].iloc[0]
            st.divider()
            doc_id = selected_data["id"]
            name = st.text_input("Name", selected_data["name"])
            location = st.text_input("Location", selected_data["location"]).strip().upper()
            address = st.text_area("Address", selected_data["address"])
            contact = st.text_input("Contact", selected_data["contact"])
            email = st.text_input("Email", selected_data["email"])
            
            options = ["SWIFTCOM", "SHREE AGENCY"]
            selected_value = selected_data["company"]
            # Find index of selected_value in options list
            index = options.index(selected_value) if selected_value in options else 0
            # Show selectbox with selected value
            company = st.selectbox("Company", options, index=index)

            st.divider()
            if st.button("Update"):
                update_distributor(doc_id, {"name": name, "location": location,"address": address, "contact": contact, "email": email, "company": company})
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

# func for add device
def add_device(data):
    db.collection("device").add(data)

#---------------------------------------------------------------------------
# --- Function to get unique brand/type values to delete device---
@st.cache_data
def get_unique_values():
    docs = db.collection("device").stream()
    brands = set()
    types = set()
    for doc in docs:
        data = doc.to_dict()
        if "brand" in data:
            brands.add(data["brand"])
        if "type" in data:
            types.add(data["type"])
    return sorted(brands), sorted(types)

def device_exists(article, model):
    # Implement your DB lookup logic here.
    # Return True if the device already exists, else False.
    pass


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
    tab_view, tab_add, tab_add_bulk, tab_delete,tab_delete_all, tab_update = st.tabs(["📱Existing Device  ", " ➕Add Device  ", " 📦➕Add Bulk Device.csv   ",  " 🗑️Delete  ", " 📦🗑️Delete All   ", "  ✏️Update  "])
    with tab_view:
                
        st.subheader("📱 Existing Devices")

        # Fetch devices from Firestore (simulate)
        docs = db.collection("device").get()
        user_data = [{**doc.to_dict(), "doc_id": doc.id} for doc in docs]

        if user_data:
            df = pd.DataFrame(user_data)
            
            # Get unique brand and type options
            brand_options = sorted(df["brand"].dropna().unique())
            type_options = sorted(df["type"].dropna().unique())
            
            # Show filters at the top
            selected_brands = st.multiselect("Filter by Brand", brand_options, default=brand_options)
            selected_types = st.multiselect("Filter by Type", type_options, default=type_options)
            
            # Filter dataframe based on selections
            filtered_df = df[
                (df["brand"].isin(selected_brands)) &
                (df["type"].isin(selected_types))
            ]
            
            # Display dataframe container below filters
            container = st.container()
            
            column_order = ["brand", "type", "model", "article", "stock"]
            ordered_columns = [col for col in column_order if col in filtered_df.columns] + \
                            [col for col in filtered_df.columns if col not in column_order and col != "doc_id"]
            
            if not filtered_df.empty:
                container.dataframe(filtered_df[ordered_columns])
            else:
                container.info("No devices match the selected filters.")
        else:
            st.info("No Device found.")



    with tab_add:
        # Simulated Firestore fetch
        docs = db.collection("device").get()
        user_data = [{**doc.to_dict(), "doc_id": doc.id} for doc in docs]
        df = pd.DataFrame(user_data)

        # Initialize session state for new entries
        #if "new_brand" not in st.session_state:
        #    st.session_state.new_brand = ""
        #if "new_type" not in st.session_state:
        #    st.session_state.new_type = ""
        col1, col2= st.columns(2,vertical_alignment="top",gap="small",border=True)
        
        with col1:  
            if not df.empty: 
                brand_options = sorted(df["brand"].dropna().unique().tolist())
                with st.popover("Add New Brand"):
                    new_brand=st.text_input("Enter New Brand Name",key="new_brand_input").strip().upper()
                    if new_brand:
                        brand_options.append(new_brand)
                        col1.markdown(f"`{new_brand} `: Added in the Brand list")
                      

        with col2:            
            if not df.empty: 
                type_options = sorted(df["type"].dropna().unique().tolist())
                with st.popover("Add New Type"):        
                    new_type = st.text_input("Enter New Type",key="new_type_input").strip().upper()
                    if new_type:
                        type_options.append(new_type)
                        col2.markdown(f"`{new_type} `: Added in the type list")
    
            



        # Add "New Brand" and "Add New" options
   
        with st.form("add_device_form"):
            # --- Brand Selection ---
            st.subheader(" ➕ Add Device")
            if not df.empty:
                selected_brand = st.selectbox("Select Brand", brand_options)
            else:
                selected_brand = st.text_input("Enter Brand").strip().upper()

            brand = selected_brand

            # --- Type Selection ---
            if not df.empty:
                selected_type = st.selectbox("Select Type", type_options)
            else:
                selected_type = st.text_input("Enter Type").strip().upper()


            dev_type = selected_type

            # Other Fields
            article = st.text_input("Article Number (if any)")
            model = st.text_input("Model")
            stock = st.text_input("Stock", "0")

            # Submit Button
            submitted = st.form_submit_button("Add Device")

            if submitted:
                if not brand or not dev_type:
                    st.warning("Please enter both a valid Brand and Type.")
                else:
                    # Here you can write to Firestore or show results
                    new_device = {
                        "brand": brand,
                        "type": dev_type,
                        "article": article,
                        "model": model,
                        "stock": stock
                    }
                    db.collection("device").add(new_device)  # Uncomment to add to Firestore
                    st.toast("Device added successfully!")
                    new_brand=None
                    new_type=None
                    
                    #st.session_state["new_brand_input"] = ""
                    #st.session_state["new_type_input"] = ""
                    #st.json(new_device)
                    #st.rerun()
    
    with tab_add_bulk:
        st.subheader("📦 Bulk Add Devices")
        st.markdown("**CSV format:** `article`,`brand`,`type`,`model`,`stock`")

        # Download template
        template_df = pd.DataFrame(columns=["article", "brand", "type", "model", "stock"])
        csv = template_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV Template", csv, "device_template.csv", "text/csv")

        # Initialize session state
        if "bulk_upload_done" not in st.session_state:
            st.session_state.bulk_upload_done = False

        # Upload filled CSV
        file = st.file_uploader("Upload your CSV", type="csv")

        # Show upload button only if file is uploaded and not already processed
        if file and not st.session_state.bulk_upload_done:
            try:
                df = pd.read_csv(file)
                required_columns = {"article", "brand", "type", "model", "stock"}

                if required_columns.issubset(df.columns):
                    with st.spinner("Adding devices..."):
                        for _, row in df.iterrows():
                            data = row.to_dict()
                            try:
                                data["stock"] = int(data["stock"])
                            except:
                                data["stock"] = 0
                            add_device(data)

                    st.success("✅ Devices added successfully.")
                    st.dataframe(df)
                    st.session_state.bulk_upload_done = True  # Set flag to prevent reprocessing
                else:
                    st.error("❌ CSV must have columns: article, brand, type, model, stock")
            except Exception as e:
                st.error(f"❌ Error reading CSV: {e}")

        # Optionally allow user to reset for a new upload
        if st.session_state.bulk_upload_done:
            if st.button("🔄 Upload Another File"):
                st.session_state.bulk_upload_done = False



    with tab_delete:
        # Fetch device data
        docs = db.collection("device").get()
        user_data = [{**doc.to_dict(), "doc_id": doc.id} for doc in docs]
        df = pd.DataFrame(user_data)

        st.header(" 🗑️ Delete Device")

        if df.empty:
            st.info("No devices available.")
        else:
            # Step 1: Select Brand
            brands = sorted(df["brand"].dropna().unique())
            selected_brand = st.selectbox("Select Brand", brands)

            # Step 2: Filter by Brand → Type
            type_df = df[df["brand"] == selected_brand]
            types = sorted(type_df["type"].dropna().unique())
            selected_type = st.selectbox("Select Type", types)

            # Step 3: Filter by Brand + Type → Model
            model_df = type_df[type_df["type"] == selected_type]
            models = sorted(model_df["model"].dropna().unique())
            selected_model = st.selectbox("Select Model", models)

            # Step 4: Filter by Brand + Type + Model → article
            article_df = model_df[model_df["model"] == selected_model]
            article = sorted(article_df["article"].dropna().unique())
            selected_article = st.selectbox("Select Article :", article)

            # Step 5: Filter by Brand + Type + Model + Color → Spec
            #spec_df = color_df[color_df["color"] == selected_color]
            #specs = sorted(spec_df["spec"].dropna().unique())
            #selected_spec = st.selectbox("Select Specification", specs)

            # Final match
            final_df = article_df[article_df["article"] == selected_article]

            if not final_df.empty:
                doc_id = final_df.iloc[0]["doc_id"]
                st.markdown(f"**Ready to delete:** `{selected_brand} | {selected_type} | {selected_model}  {selected_article}`")

                if st.button("Delete Device"):
                    db.collection("device").document(doc_id).delete()
                    st.success("Device deleted successfully!")
                    st.rerun()
            else:
                st.warning("Matching device or article not found.")


    with tab_delete_all:
        # --- Delete filtered devices ---
        def delete_filtered_devices(selected_brands, selected_types):
            docs = db.collection("device").stream()
            count = 0
            for doc in docs:
                data = doc.to_dict()
                brand_match = not selected_brands or data.get("brand") in selected_brands
                type_match = not selected_types or data.get("type") in selected_types
                if brand_match and type_match:
                    doc.reference.delete()
                    count += 1
            return count

        # --- UI ---
        st.subheader("🗑️ Delete Devices  by Filter")

        brands, types = get_unique_values()

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_brands = st.multiselect("Select Brand(s)", brands)
        with col2:
            selected_types = st.multiselect("Select Type(s)", types)

        # Show selected filters
        st.markdown(f"**Selected brands:** `{', '.join(selected_brands) or 'All'}`")
        st.markdown(f"**Selected types:** `{', '.join(selected_types) or 'All'}`")

        # Delete button
        if st.button("🚨 Delete Filtered Devices"):
            with st.spinner("Deleting..."):
                deleted_count = delete_filtered_devices(selected_brands, selected_types)
            st.success(f"✅ Deleted {deleted_count} matching device(s).")
            time.sleep(5)
            st.rerun()


    with tab_update:
        # Load data from Firestore
        docs = db.collection("device").get()
        user_data = [{**doc.to_dict(), "doc_id": doc.id} for doc in docs]
        df = pd.DataFrame(user_data)

        st.header(" ✏️ Update Device")

        if df.empty:
            st.info("No devices available.")
        else:
            # Step 1: Select Brand
            brands = sorted(df["brand"].dropna().unique())
            selected_brand = st.selectbox("Select Brand", brands, key="brand_select")

            # Step 2: Filter by Brand → Type
            type_df = df[df["brand"] == selected_brand]
            types = sorted(type_df["type"].dropna().unique())
            selected_type = st.selectbox("Select Type", types, key="type_select")

            # Step 3: Filter by Brand + Type → Model
            model_df = type_df[type_df["type"] == selected_type]
            models = sorted(model_df["model"].dropna().unique())
            selected_model = st.selectbox("Select Model", models, key="model_select")

            # Step 4: Filter by Brand + Type + Model → Color
            #color_df = model_df[model_df["model"] == selected_model]
            #colors = sorted(color_df["color"].dropna().unique())
            #selected_color = st.selectbox("Select Color", colors, key="color_select")

            # Step 5: Filter by Brand + Type + Model + Color → Spec
            #spec_df = color_df[color_df["color"] == selected_color]
            #specs = sorted(spec_df["spec"].dropna().unique())
            #selected_spec = st.selectbox("Select Specification", specs, key="spec_select")

            # Final filtered record
            final_df = model_df[model_df["model"] == selected_model]

            if not final_df.empty:
                record = final_df.iloc[0]
                doc_id = record["doc_id"]

                st.markdown("### Edit Device Fields")

                # Editable input fields with unique keys
                new_brand = st.text_input("Brand", value=record["brand"], key="edit_brand")
                new_type = st.text_input("Type", value=record["type"], key="edit_type")
                new_model = st.text_input("Model", value=record["model"], key="edit_model")
                new_article = st.text_input("Article", value=record["article"], key="edit_article")
                new_stock = st.text_area("Stock", value=record["stock"], key="edit_stock")

                if st.button("Update Device", key="update_button"):
                    db.collection("device").document(doc_id).update({
                        "brand": new_brand.strip().upper(),
                        "type": new_type.strip().capitalize(),
                        "model": new_model.strip(),
                        "article": new_article.strip(),
                        "stock": new_stock.strip()
                    })
                    st.success("Device updated successfully!")
                    st.rerun()
            else:
                st.warning("Matching device not found.")
        
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
