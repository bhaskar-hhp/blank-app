import streamlit as st
import pandas as pd
#import firebase_admin
#from firebase_admin import credentials, firestore, initialize_app
import io
from io import StringIO
from datetime import datetime, timedelta
import time
import uuid
from PIL import Image
import os
import base64
import json
from pymongo import MongoClient


#Page title
st.set_page_config(
   page_title="Swiftcom DMS",
   page_icon=":material/bar_chart:",
   layout="wide",
   initial_sidebar_state="expanded",
)
# HF codes
#firebase_key = os.environ["FIREBASE_KEY"]
#cred = credentials.Certificate(json.loads(firebase_key))

# Streamlit, Google Cloud
#cred = credentials.Certificate("firebase_key.json")

# Render
#cred = credentials.Certificate("/etc/secrets/firebase_key.json")

# Initialize Firestore codespace in .toml file
#    cred = credentials.Certificate(dict(st.secrets["firebase"]))


# Initialize Firebase
# if not firebase_admin._apps:

#     try:
#         #adding Mongodb Connecttion & Collection for Firebase - Render
#         cred = credentials.Certificate("/etc/secrets/firebase_key.json")
        
#     except Exception:
#         #adding Mongodb Connecttion & Collection for Firebase - Streamlit
#         cred = credentials.Certificate(dict(st.secrets["firebase"]))


#     # Initialize the Firebase app
#     firebase_admin.initialize_app(cred)

try:
    #adding Mongodb Connecttion & Collection for MongoDB - Render
    uri = os.environ["MONGODB_URI"]
    db_name = os.environ["MONGODB_DB"]

except Exception:
    #adding Mongodb Connecttion & Collection for MongoDB - Streamlit
    uri = st.secrets["mongodb"]["uri"]
    db_name = st.secrets["mongodb"]["db"]
    

# Initialize the MongoDB app
client = MongoClient(uri)
db = client[db_name]  # DB group name
dist_collection = db["Dist"]     # Collection name
users_collection = db["users"]
device_collection = db["devices"]
log_collection = db["logs"]
order_collection = db["order"]

# Initialize Firestore
#db = firestore.client()


# log file def
def log_event(level, message):
    log_collection.insert_one({
        "timestamp": datetime.now(),   
        "level": level,
        "message": message
    })

# Convert the local image to base64
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# -------------------------------
# 🔐 LOGIN SECTION
# -------------------------------
#st.dialog("🔐 Login")
def login():
    col1,col2,col3=st.columns([1,2,1],vertical_alignment="center")
    with col1:
        st.markdown(
            """
            <style>
            @keyframes fadeSlideIn {
                0% {
                    opacity: 0;
                    transform: translateY(30px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes colorPulse {
                0% {
                    color: #008CBA;
                }
                50% {
                    color: #00BFFF;
                }
                100% {
                    color: #008CBA;
                }
            }

            .logo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: Center;
                animation: fadeSlideIn 1s ease-out forwards;
                line-height: .8;  /* tight spacing */
                margin-bottom: 10px;
                
            }

            .logo-swiftcom {
                font-size: 36px;
                font-weight: bold;
                color: #b0160f;
                text-shadow: 3px 2px 2px #00000040;
                margin: 0;
                padding: 0;
            }

            .logo-dms {
                font-size: 20px;
                font-weight: 600;
                letter-spacing: 3px;
                animation: colorPulse 2s infinite;
                margin: 0;
                padding: 0;
            }
            </style>

            <div class='logo-container'>
                <div class='logo-swiftcom'>SWIFTCOM</div>
                <div class='logo-dms'>    DMS</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:


        
        
        with st.form("login_form"):
            st.subheader("🔐 Login",divider=True)
            login_type = st.radio("",("👥Members","🤝Partners"),horizontal=True)
            #st.divider()

            username = st.text_input("Username").strip().upper()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login",use_container_width=True)
            
            if submitted:
                if login_type == "👥Members":
                    
                    query = users_collection.find_one({"name": username, "pass": password})
                    
                    if query:
                        
                        st.session_state.logged_in = True
                        st.session_state.username = query.get("name", username)
                        st.session_state.user_role = query.get("type", "Standard")
                        st.success(f"Welcome, {st.session_state.username}!")
                        log_event("LOGIN", st.session_state.username)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        log_event("LOGIN", f"Login Fail {username}")        
                        
                elif login_type == "🤝Partners":
                    if username.isdigit():
                        # do 1: username is all digits, treat as int
                        user_data = dist_collection.find_one({"id": int(username), "pwd": password})
                        if not user_data:
                            user_data = dist_collection.find_one({"id": username, "pwd": password})  

                    else:
                        # do 2: username has non-digit chars
                        user_data = dist_collection.find_one({"id": username, "pwd": password})
                                        
                    if user_data:                    
                        st.session_state.logged_in = True
                        st.session_state.username = user_data.get("name", username)
                        st.session_state.user_role = "Guest"
                        st.success(f"Welcome, {username}!")
                        log_event("LOGIN", st.session_state.username)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.1") 
                        log_event("LOGIN", "Login Fail {username}")                                              
                else:
                    st.error("Invalid username or password.2") 
                    log_event("LOGIN", "Login Fail {username}")                  
            else:
                if not username and password:
                    st.error("Invalid login type")
                    log_event("LOGIN", "Login Fail {username}")

# -------------------------------
# 🚪 LOGOUT FUNCTION
# -------------------------------
def logout():
    log_event("LOGOUT", st.session_state.username)
    for key in ["logged_in", "username", "user_role", "selected_page", "user_option", "dist_option"]:
        st.session_state.pop(key, None)
    st.success("Logged out successfully.")
    
    st.rerun()

# Inject custom CSS


# Path to your uploaded image
img_path = "sback.jpg"
img_base64 = get_base64(img_path)

# Inject CSS for sidebar background image
st.markdown(
    f"""
    <style>
    section[data-testid="stSidebar"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: left;
        color: #002233
    }}

    
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        display: block;
        text-align: center;
                 
        height: 45px;
        font-size: 10px;
        background: linear-gradient(0deg, #062134, #8fc3e7);
        margin-bottom: 5px;
        margin-top: 10px;
        color: white;
        border: none;
        border-radius: 10px;
        display: flex;
        justify-content: center;    
        align-items: center;
        position: relative;
    }

    div.stButton > button:hover {
        background: linear-gradient(180deg, green, lightgreen);
    }
            
    div.stVerticalBlock {
        display: block;
        
            }

    .stApp {
        background: linear-gradient(10deg, lightblue, #DFECF3);    
        background-color: #DFECF3;
        font-family: 'Arial', sans-serif;
    }

            

    
    [data-testid="stHeader"]{
        
        background-color: rgba(0,0,0,0);

    }

/*local st.container - view user - user names*/
div.st-emotion-cache-1d8vwwt {
            background: linear-gradient(135deg, lightblue, white);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            max-width: 100%;
            margin-top: 20px;
            color: Black;
           
            } 

/*live st.container - view user - user names*/
div.st-emotion-cache-o29vc0 {
            background: linear-gradient(135deg, lightblue, white);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            max-width: 100%;
            margin-top: 20px;
            color: Black;
           
            }
                 
/*for local container*/
div.stColumn.st-emotion-cache-1ot6vu8.e1lln2w82 {
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            margin-top: 10px;
            margin-bottom: 30px;
            
            }

/* 2-lv live st.expander - Update Order page (it's working with most of the container)*/
div.stExpander.st-emotion-cache-8atqhb {
            background: linear-gradient(135deg, lightblue, white);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            max-width: 100%;
            margin-top: 5px;
            color: Black;
           
            }
                 
/* 2-lc Local st.expander - Update Order page (it's working with most of the container)*/
div.st-emotion-cache-0 {
            background: linear-gradient(135deg, lightblue, white);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            max-width: 100%;
            margin-top: 5px;
            color: Black;
           
            }
 
/*for Live app container*/ 
div.stColumn.st-emotion-cache-1cnjs0b.eertqu01 {
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            margin-top: 10px;
            margin-bottom: 30px;

            } 

/*for Live app container 
div.st-emotion-cache-1clstc5.eah1tn14{
            background: linear-gradient(135deg, lightblue, white);
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            margin-top: 10px;
            margin-bottom: 30px;
            border-radius: 10px;
            
            } */
            
/*for local container
div.st-emotion-cache-1clstc5.e1kosxz24  {
            background: linear-gradient(135deg, lightblue, white);
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            margin-top: 10px;
            margin-bottom: 30px;
            border-radius: 10px;
           } /*                         

/*for Live app container user name row-expander*/             
.st-emotion-cache-4rp1ik.eah1tn13 {
            background: linear-gradient(0deg, lightblue, white);
            box-shadow: 1px 1px 5px rgba(1, 0, 0, .2);
            margin-top: 0px;
            margin-bottom: 5px;
            border-radius: 10px;
            }

/*for local container user name row-expander          
.st-emotion-cache-4rp1ik.e1kosxz23 {
            background: linear-gradient(0deg, lightblue, white);
            box-shadow: 1px 1px 5px rgba(1, 0, 0, .2);
            margin-top: 0px;
            margin-bottom: 3px;
            border-radius: 10px;
            
             }*/
            
/*for local container user name row-expander-backborder 
.st-emotion-cache-1h9usn1 {
            border-style: none;
            }
*/

/*for Live app container user name row-expander-backborder
.st-emotion-cache-1h9usn1 {
            border-style: none;
            }
*/
            
/*for local container summary "🎯 2 active user(s) matched with selected brands.        
.st-emotion-cache-ao4qku.e1rzn78k0 {
            display: flex;
            justify-content: center;
            background: linear-gradient(180deg, #0a5668, #498fa0);
            box-shadow: 1px 1px 5px rgba(1, 0, 0, .2);
            margin-top: 0px;
            margin-bottom: 30px;
            border-radius: 10px;
            align-items: center;
            color : white;
            padding: 1px;
            }*/


/*for Live App container summary "🎯 2 active user(s) matched with selected brands.        
.st-emotion-cache-uzemrq.e1chbk300 {
            display: flex;
            justify-content: center;
            background: linear-gradient(180deg, #0a5668, #498fa0);
            box-shadow: 1px 1px 5px rgba(1, 0, 0, .2);
            margin-top: 0px;
            margin-bottom: 30px;            
            align-items: center;
            color : white;
            padding: 1px;
            }*/
           

/*for local App & Live App both - User ID PIC container*/  
.st-emotion-cache-7czcpc.evl31sl1 {
            margin-top: 65px;
            margin-left: 30px;
            box-shadow: 1px 1px 5px rgba(1, 0, 0, 1.2);
            /*clip-path: circle(50% at 50% 50%); */  
            padding: 5px;
            border-radius: 10px;
            }

/*for local App & Live App both - selectBox*/              
div[data-baseweb="select"] {
        font-size: 10px;
    }


            


    </style>
""", unsafe_allow_html=True)


st.markdown(
    f"""
    <br>
    
    <style>
        
        [data-testid="stForm"] {{
            background: linear-gradient(135deg, lightBlue, #DBE0E2);
            
            padding: 30px;
            border-radius: 30px;
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            max-width: 100%;
            margin-top: 20px    ;
            color: Black;
        }}

        /* To make button Redesign*/            
        [data-testid="stBaseButton-secondaryFormSubmit"]{{
            margin: 0 auto;
            display: block; /* to set button @ Center*/
            background: linear-gradient(10deg, lightgreen, green);
            box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
            padding: 8px 16px;
            margin-top: 20px;
            border-radius: 30px;
            width: 50%;
            padding: 15px;
        }}
        

    </style>
        """,unsafe_allow_html=True
)


# -------------------------------
# 🧭 SIDEBAR NAVIGATION
# -------------------------------
def show_sidebar():
    user_role = st.session_state.get("user_role")
    with st.sidebar:

        st.markdown(
            """
            <style>
            @keyframes fadeSlideIn {
                0% {
                    opacity: 0;
                    transform: translateY(30px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes colorPulse {
                0% {
                    color: #008CBA;
                }
                50% {
                    color: #00BFFF;
                }
                100% {
                    color: #008CBA;
                }
            }

            .logo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: Center;
                animation: fadeSlideIn 1s ease-out forwards;
                line-height: .8;  /* tight spacing */
                margin-bottom: 10px;
                
            }

            .logo-swiftcom {
                font-size: 36px;
                font-weight: bold;
                color: #b0160f;
                text-shadow: 3px 2px 2px #00000040;
                margin: 0;
                padding: 0;
            }

            .logo-dms {
                font-size: 20px;
                font-weight: 600;
                letter-spacing: 3px;
                animation: colorPulse 2s infinite;
                margin: 0;
                padding: 0;
            }
            </style>

            <div class='logo-container'>
                <div class='logo-swiftcom'>SWIFTCOM</div>
                <div class='logo-dms'>    DMS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        #st.divider()
        st.markdown(
            f"""
            <div style='text-align: center; font-weight: bold;'>
                👤 <span style='color: blue;'>{st.session_state.get('username')}</span> <span style='color: green;'>({user_role})</span>
            </div>
            """,
            unsafe_allow_html=True
        )        
        st.divider()
        st.title("📂 Navigation")

        # All roles: Home
        if st.button("🏠 Home",use_container_width=True):
            st.session_state.selected_page = "Home"


        # Admin , "Standard", "Back Office": -----------------------------------------------------------------------------
        if user_role in ["Admin"]:
            if st.button("🕒 Attendance",use_container_width=True):
                st.session_state.selected_page = "Attendance"



        # Admin , "Standard", "Guest": -----------------------------------------------------------------------------
        if user_role in ["Standard"]:
            if st.button("📦Purchase Order",use_container_width=True):
                st.session_state.selected_page = "Order"
                

        # Admin , Back Office: -----------------------------------------------------------------------------
        if user_role in ["Admin", "Back Office"]:
            with st.sidebar.expander(f" **Back Office Options** "):
                if st.button("📦 Update Order",use_container_width=True):
                    st.session_state.selected_page = "Update Order"
                if st.button("📱 Devices",use_container_width=True):
                    st.session_state.selected_page = "Devices"
                if st.button("📊 Distributors",use_container_width=True):
                    st.session_state.selected_page = "Distributors"
                if st.button("📒 Ledgers",use_container_width=True):
                    st.session_state.selected_page = "Distributors Ledgers"
                if st.button("👥 Assign User",use_container_width=True):
                    st.session_state.selected_page = "Assign User"

                #if st.button("🚚 Logistics"):
                #    st.session_state.selected_page = "Logistics"

        # Admin Only --------------------------------------------------------------------------------------
        if user_role in ["Admin"]:
            with st.sidebar.expander(f" **Admin Options** "):
                if st.button("📦 Order.set",use_container_width=True):
                    st.session_state.selected_page = "Manage Order"
                if st.button("👥 Users",use_container_width=True):
                    st.session_state.selected_page = "Users"
                if st.button("Utility",use_container_width=True, icon="🛠️"):
                    st.session_state.selected_page = "Utility"
                if st.button("Attendance.s",use_container_width=True,icon="🕒"):
                    st.session_state.selected_page = "Attendance Managment"
                if st.button("📜 Logs",use_container_width=True):
                    st.session_state.selected_page = "Logs"


        # Guest Only --------------------------------------------------------------------------------------
        if user_role in ["Guest"]:
            if st.button("📝 Ledger",use_container_width=True):
                st.session_state.selected_page = "Ledger"
            if st.button("📦Purchase Order",use_container_width=True):
                st.session_state.selected_page = "Orders"
     
        # --------------------------------------------------------------------------------------------------

        # Standard Only --------------------------------------------------------------------------------------
        if user_role in ["Standard"]:
            if st.button("📝 Ledgers",use_container_width=True):
                st.session_state.selected_page = "Ledgers"
     
        # --------------------------------------------------------------------------------------------------


        if st.button("🔐 Change Password",use_container_width=True):
            st.session_state.selected_page = "Change_Password"

        # Logout button
        if st.button("🚪 Logout",use_container_width=True):
            logout()

# -------------------------------
# 🌐 PAGE CONTENT
# -------------------------------
def home_page():

    st.markdown(
        f"""
        
        <h2 style='
        background: linear-gradient(1deg, Lightblue, white);
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:black; 
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        🏠 Home Page 
        </h2>
        <h6 style='text-align: center;'> Welcome ! <span style='font-weight:bold; color: blue;'>{st.session_state.username}</span> to the Home Page</h6>
        <br>

        

        """,
        unsafe_allow_html=True
    )




# Users Management with radio options

def users_page():
    user_role = st.session_state.get("user_role")
    if user_role not in ["Admin", "Standard"]:
        st.error("Access denied.")
        return

    #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        📝 User Management
        </h5>
        <br>
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
        #st.divider()

    


    # Add User
    if user_option == "Add User":
        st.subheader("Add New User")
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        with st.form("add_user_form"):
            col1, col2 = st.columns([1, 3], gap="small")
            with col1:
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
                name = st.text_input("User Name").strip().upper()
                user_type = st.selectbox("Type", ["Admin", "Back Office", "Standard", "Guest"])
                password = st.text_input("Password", type="password")

            with st.expander("Add additional user details"):
                col3, col4 = st.columns(2, gap="small")
                with col3:
                    
                    full_name = st.text_input("Full Name").strip().upper()
                    doj_in = st.date_input("Date of Joining")
                    dob_in = st.text_input("Date of Birth")
                    status = st.selectbox("Status", ["Active", "Inactive"])
                    contact = st.text_input("Contact").strip().upper()
                    work_area = st.text_input("Work Area").strip().upper()
                    work_profile = st.text_input("Work Profile").strip().upper()
                    Brand = st.text_input("Brand").strip().upper()
                with col4:
                    fname = st.text_input("Father's Name").strip().upper()
                    address = st.text_area("Address").strip().upper()
                    email = st.text_input("Email").strip().upper()
                    doc_url = st.text_input("Document URL").strip()
                    Closing_Date_in = st.date_input("Closing Date")

            submitted = st.form_submit_button("Submit",use_container_width=True)

            if submitted:
                all_users = list(users_collection.find())
                name_exists = any(user.get("name") == name for user in all_users)
                max_id = max([user.get("id", 0) for user in all_users], default=0)

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
                    user_data = {
                        "id": new_id,
                        "image_b64": image_b64,
                        "name": name,
                        "type": user_type,
                        "pass": password,
                        "full_name": full_name,
                        "doj": doj_in.strftime("%d-%m-%Y"),
                        "dob": dob_in,
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
                    users_collection.insert_one(user_data)
                    st.success(f"✅ User '{name}' added with ID {new_id}.")

    elif user_option == "View User":
        st.subheader("📋 View Users Database")
        all_users = list(users_collection.find())

        brand_options = sorted(set(user.get("Brand", "N/A") for user in all_users if user.get("Brand")))
        col_brand, col_type=st.columns(2,border=True)
        with col_brand:
            selected_brands = st.multiselect("Select Brands to filter", brand_options, default=brand_options)
        with col_type:
            selected_type = st.selectbox("Select Type to filter", ["Admin", "Back Office", "Standard", "Guest"])
        
        
        tab1, tab2, tab3 = st.tabs(["🟢 Active Users", "🔴 Inactive Users", "❔ No Status Users"])

        def show_users(users_list):
            for data in users_list:
                with st.container():
                    
                    with st.expander(f" **{data.get('full_name', 'N/A')}**  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 💼 Brand: **{data.get('Brand', 'N/A')}**",icon="👤"):
                        cols = st.columns([1, 3])
                        with cols[0]:
                            if data.get("image_b64"):
                                img_bytes = base64.b64decode(data["image_b64"])
                                st.image(img_bytes, width=80)
                            else:
                                st.write("❌ No Image")

                        with cols[1]:
                            c1, c2 = st.columns(2, gap="small")
                            with c1:
                                st.markdown(f"**👤 User Name:** {data.get('name', 'N/A')}")
                                st.markdown(f"**🧑‍💻 Type:** {data.get('type', 'N/A')}")
                                st.markdown(f"**📌 Status:** {data.get('status', '❌ Not Set')}")
                            with c2:
                                st.markdown(f"**📅 Date of Joining:** {data.get('doj', 'N/A')}")
                                st.markdown(f"**📅 Date of Birth:** {data.get('dob', 'N/A')}")
                                st.markdown(f"**📞 Contact:** {data.get('contact', 'N/A')}")
                            st.divider()
                            c3, c4 = st.columns(2, gap="small")
                            with c3:
                                st.markdown(f"**💼 Work Area:** {data.get('work_area', 'N/A')}")
                                st.markdown(f"**💼 Work Profile:** {data.get('work_profile', 'N/A')}")
                                st.markdown(f"**📧 Email:** {data.get('email', 'N/A')}")
                                st.markdown(f"**📅 Closing Date:** {data.get('Closing_Date', 'N/A')}")
                            with c4:
                                st.markdown(f"**👤 Father Name:** {data.get('fname', 'N/A')}")
                                st.markdown(f"**🏠 Address:** {data.get('address', 'N/A')}")
                                doc_url = data.get("doc_url")
                                if doc_url:
                                    st.link_button("📄 Open Document", doc_url,type="primary")
                                else:
                                    st.write("❌ No Document URL")
                        #st.markdown("</div>", unsafe_allow_html=True)

        with tab1:
            active_users = [u for u in all_users if u.get("status", "").lower() == "active" and u.get("Brand") in selected_brands and u.get("type") == selected_type]
            if active_users:
                st.markdown(f"""
                    <div style='
                        display: flex;
                        justify-content: center;
                        background: linear-gradient(180deg, #0a5668, #498fa0);
                        box-shadow: 1px 1px 5px rgba(1, 0, 0, .2);
                        margin-top: 0px;
                        margin-bottom: 30px;
                        border-radius: 10px;
                        align-items: center;
                        color : white;
                        padding: 1px;
                    '>
                        🎯 {len(active_users)} active user(s) matched with selected brands.
                    </div>
                """, unsafe_allow_html=True)
                

                show_users(active_users)
            else:
                st.info("No active users found.")

        with tab2:
            inactive_users = [u for u in all_users if u.get("status", "").lower() == "inactive" and u.get("Brand") in selected_brands and u.get("type") == selected_type]
            if inactive_users:
                st.write(f"🎯 {len(inactive_users)} `inactive user(s) matched with selected brands.`")
                show_users(inactive_users)
            else:
                st.info("No inactive users found.")

        with tab3:
            no_status_users = [u for u in all_users if not u.get("status") or not u.get("Brand")]
            if no_status_users:
                st.write(f"🎯 {len(no_status_users)} ` user(s) found without STATUS or BRAND selected.`")
                show_users(no_status_users)
            else:
                st.info("All users have status set.")

    elif user_option == "Delete User":
        st.subheader("🗑️ Delete User")
        all_users = list(users_collection.find())
        usernames = [u.get("name") for u in all_users]
        to_delete = st.selectbox("Select user to delete", usernames)
        if st.button("Delete",type="primary", use_container_width=True):
            users_collection.delete_one({"name": to_delete})
            st.success(f"Deleted user {to_delete}.")

    elif user_option == "Update User":
        st.subheader("✏️ Update User")
        all_users = list(users_collection.find())
        usernames = [u.get("name") for u in all_users]
        selected_user = st.selectbox("Select User to Update", usernames)
        user_data = users_collection.find_one({"name": selected_user})
        image_file = st.file_uploader("Upload New Image (optional)", type=["png", "jpg", "jpeg"])

        with st.form("update_user_form"):
            col1, col2 = st.columns([1, 3], gap="small")
            with col1:
                if image_file:
                    image = Image.open(image_file)
                    st.image(image, caption="Preview", width=150)
                elif user_data.get("image_b64"):
                    st.image(base64.b64decode(user_data["image_b64"]), width=150)
                else:
                    st.write("❌ No image available")

            with col2:
                name = st.text_input("User Name", value=user_data.get("name", "")).strip().upper()
                user_type = st.selectbox("Type", ["Admin", "Back Office", "Standard", "Guest"], index=["Admin", "Back Office", "Standard", "Guest"].index(user_data.get("type", "Standard")))
                password = st.text_input("Password", value=user_data.get("pass", ""), type="password")

            with st.expander("Update additional user details"):
                col3, col4 = st.columns(2, gap="small")
                with col3:
                    full_name = st.text_input("Full Name", value=user_data.get("full_name", "")).strip().upper()
                    doj = st.text_input("Date of Joining", value=user_data.get("doj", ""))
                    dob = st.text_input("Date of Birth", value=user_data.get("dob", ""))
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
                    Closing_Date = st.text_input("Closing Date", value=user_data.get("Closing_Date", ""))

            submitted = st.form_submit_button("Update User",use_container_width=True)

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
                    "doj": doj,
                    "dob": dob,
                    "status": status,
                    "contact": contact,
                    "work_area": work_area,
                    "work_profile": work_profile,
                    "Brand": Brand,
                    "fname": fname,
                    "address": address,
                    "email": email,
                    "doc_url": doc_url,
                    "Closing_Date": Closing_Date
                }
                users_collection.update_one({"name": selected_user}, {"$set": updated_data})
                st.success(f"✅ User '{name}' updated successfully.")
 #-----------------------------------------Distributors placeholder

def distributors_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        return
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        📊 Distributors
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    # COLLECTION = "Dist"

    # # Firebase operations
    # def add_distributor(data):
    #     db.collection(COLLECTION).add(data)

    # def get_distributors():
    #     docs = db.collection(COLLECTION).stream()
    #     return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    # def update_distributor(doc_id, data):
    #     db.collection(COLLECTION).document(doc_id).update(data)

    # def delete_distributor(doc_id):
    #     db.collection(COLLECTION).document(doc_id).delete()

    # Streamlit UI
    
    option = st.radio("Select Operation", ["View", "Add", "Bulk Add", "Update", "Delete"],horizontal=True)
    st.divider()

    if option == "View":
        st.subheader("View Distributors")
        view_data=dist_collection.find({},{"_id":0})
        #st.dataframe(view_data)

        if view_data:           
            st.dataframe(view_data)
        else:
            st.info("No distributors found.")

    elif option == "Add":
        st.subheader("Add Distributor")
        
        dist_location=dist_collection.find({},{"_id":0, "location":1})
        location = sorted({doc["location"].upper() for doc in dist_location if "location" in doc and doc["location"]})
        col_loc,col_new_loc=st.columns(2,gap="small",border=True)
        with col_loc:
            loc = st.selectbox("Location", location)
        with col_new_loc:
            st.write("if location not in the list, prefer add new location Checkbox[]")

            if st.checkbox("Add New Loaction"):
                location = st.text_input("Location").strip().upper()
            else:
                location = loc

        st.divider()
        col_user_left, col_user_mid, col_user_right = st.columns(3,gap="small",border=True)
        with col_user_left:
            id = st.text_input("Login ID")
            pwd = st.text_input("Password", type="password")
        with col_user_mid:
            name = st.text_input("Name")
            address = st.text_area("Address (multiline)")
            contact = st.text_input("Contact")
            email = st.text_input("Email")
        with col_user_right:
            company = st.selectbox("Company", ["SWIFTCOM", "SHREE AGENCY"])
            #assigned_to = st.text_input("Assigned To <User Name>")
            brand = st.text_input("Brand")

        st.divider()

        doc = {
            "location": location,
            "id": id,
            "pwd": pwd,
            "name": name,
            "address": address,
            "contact": contact,
            "email": email,
            "company": company,
            #"assigned_to": assigned_to,
            "brand": brand
        }

        if st.button("Add", use_container_width=True):
            if all([id, pwd, name, location, company, brand]):
                dist_collection.insert_one(doc)
                st.success("Distributor added.")
            else:
                col_left, col_right = st.columns(2)
                with col_right:
                    if not id:
                        st.warning("* Login ID : ")

                    if not pwd:
                        st.warning("* Password : ")

                    if not name:
                        st.warning("* Name : ")

                    if not location:
                        st.warning("* Location : ")

                    if not company:
                        st.warning("* Company : ")

                    if not brand:
                        st.warning("* Brand : ")
                with col_left:
                    st.error(" Please fill all the required field. ->")

    elif option == "Bulk Add":
        st.subheader("Bulk Add Distributors (CSV)")
        st.markdown("CSV columns: id, pwd, name, location, address, contact, email, company, brand, assigned_to")
        # Download CSV template
        template_df = pd.DataFrame(columns=["id", "pwd","name", "location", "address", "contact", "email", "company", "brand", "assigned_to"])
        csv = template_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV Template", csv, "distributor_template.csv", "text/csv")

        # Upload CSV
        required_cols = ["id", "pwd", "name", "location", "address", "contact", "email", "company", "brand", "assigned_to"]

        file = st.file_uploader("Upload CSV", type="csv")

        if file:
            df = pd.read_csv(file, encoding='utf-8')

            if all(col in df.columns for col in required_cols):
                bulk_data = []
                for _, row in df.iterrows():
                    # Clean and prepare each row
                    doc = {k: str(v).strip() if pd.notna(v) else "" for k, v in row.to_dict().items()}
                    doc["location"] = doc.get("location", "").upper()  # make location UPPERCASE
                    bulk_data.append(doc)

                if bulk_data:
                    dist_collection.insert_many(bulk_data)
                    st.success("Bulk upload complete.")
                else:
                    st.warning("No valid data found in the uploaded CSV.")
            else:
                missing = [col for col in required_cols if col not in df.columns]
                st.error(f"CSV is missing required columns: {', '.join(missing)}")

    elif option == "Update":
        st.subheader("Update Distributor")
        dist_data = dist_collection.find({}, {"_id": 0, "name": 1}).sort("name", 1)
        if dist_data:            
            selected = st.selectbox("Select Distributor by Name", dist_data,index=None, placeholder="- Select Name -")
           
            if selected is not None: 
                selected_data = dist_collection.find_one({"name": selected}, {"_id": 0})
            
                st.warning(f"Selected Distributor Details :   '**{selected}**'")
                st.divider()
                col_left, col_mid,col_right = st.columns(3)
                with col_left:
                    id = st.text_input("ID", selected_data["id"])
                    pwd = st.text_input("Password", selected_data["pwd"], type="password")
                    location = st.text_input("Location", selected_data["location"]).strip().upper()
                with col_mid:
                    name = st.text_input("Name", selected_data["name"])               
                    address = st.text_area("Address", selected_data["address"])
                    contact = st.text_input("Contact", selected_data["contact"])
                    email = st.text_input("Email", selected_data["email"])
                with col_right:                                
                    options = ["SWIFTCOM", "SHREE AGENCY"]
                    selected_value = selected_data["company"]
                    # Find index of selected_value in options list
                    index = options.index(selected_value) if selected_value in options else 0
                    # Show selectbox with selected value
                    company = st.selectbox("Company", options, index=index)

                    brand= st.text_input("Brand", selected_data["brand"])
                    #assigned_to = st.text_input("Assigned To", selected_data["assigned_to"])

                st.divider()
                if st.button("Update", use_container_width=True):
                    # Build the update document
                    update_fields = {
                        "id": id,
                        "pwd": pwd,
                        "name": name,
                        "location": location,
                        "address": address,
                        "contact": contact,
                        "email": email,
                        "company": company,
                        #"assigned_to": assigned_to,
                        "brand": brand
                    }

                    # Perform the update using MongoDB
                    result = dist_collection.update_one(
                        {"name": name},     # Make sure doc_id is the _id of the document
                        {"$set": update_fields}
                    )

                    if result.modified_count:
                        st.success("Distributor updated successfully.")
                    else:
                        st.info("No changes were made (data may be identical).")
            else:
                st.info("No distributors available.")

    elif option == "Delete":
        st.subheader("Delete Distributor Update Pending Mongodb")
        dist_name=dist_collection.find({},{"_id":0, "name":1})
        
        if dist_name:
            selected = st.selectbox("Select Distributor to Delete", dist_name, index=None, placeholder="- Select Name -")
            if st.button("Delete",type="primary", use_container_width=True):
                dist_collection.delete_one({"name": selected})
            
                st.success(f"Distributor deleted : '**{selected}**' ")
        else: 
            st.info("No distributors to delete.")


# ---------------------------------------------------------------Distributors Ledgers Page----------------------
def distributors_ledgers_page():

    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        return
        #---------------------- individual page title------------------
   
    #st.header("📊 Distributors Ledgers")

    # --- Fetch ledger entries ---
    
    

    #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        📒 Distributors Ledger Viewer
            </h5>
        <br>
        """,
        unsafe_allow_html=True
    )

    #st.divider()
    #----------------------------------------------------------------
    


    # Google Drive file IDs
    file_id = '10NP-jpsSO81Uk_Ms9H_llXmddg6x0xg_'
    bal_file_id = '15wpT8PWvfhTHrefwXxcqWq5j1dDUoscm'

    # Construct direct download URLs
    csv_url = f'https://drive.google.com/uc?id={file_id}'
    bal_csv_url = f'https://drive.google.com/uc?id={bal_file_id}'

    # Load CSVs
    df = pd.read_csv(csv_url)
    bal_df = pd.read_csv(bal_csv_url)

    tab1, tab2, tab3=st.tabs(["💰 Ledger Balance", "📖 Daybook", "📘 Ledger & Voucher"])

    with tab1:
        st.info("Tab Selected : 💰 Ledger Balance")
        #st.write("🔍 Select ")

        colb, colc = st.columns(2, border=True)
        with colb:
            # --- UI Filters: Company ---
            brand_cursor = dist_collection.find({}, {"_id": 0, "brand": 1})
            brand_list = sorted({doc["brand"] for doc in brand_cursor if "brand" in doc and doc["brand"]})
            selected_brand = st.selectbox("Select Brand :", brand_list, index=None, placeholder="- Select brand - ")
        with colc:
            filter_location_check=st.checkbox("Filter location")

            if filter_location_check:
                # --- UI Filters: Location ---
                location_cursor=dist_collection.find({"brand":selected_brand},{"_id":0, "location":1})
                location_list = sorted({doc["location"] for doc in location_cursor if "location" in doc and doc["location"]})
                selected_location=st.selectbox("Select Location :", location_list, index=None, placeholder="- Select location - ")
                if selected_location:
                    filtered_ledgers = dist_collection.find({"brand": selected_brand, "location": selected_location}, {"_id": 0, "name": 1})
                    final_ledgers = [doc["name"] for doc in filtered_ledgers if "name" in doc]
                else:
                    final_ledgers = []
            else:
                # --- UI Filters: Brand ---
                    if selected_brand:
                        filtered_ledgers = dist_collection.find({"brand": selected_brand}, {"_id": 0, "name": 1})
                        final_ledgers = [doc["name"] for doc in filtered_ledgers if "name" in doc]
                    else:
                        final_ledgers = []

        search_button=st.button("🔍 Search", use_container_width=True)
        if search_button:
            st.divider()
        
            # --- Load balance CSV from Google Drive ---
            csv_url = "https://drive.google.com/uc?id=15wpT8PWvfhTHrefwXxcqWq5j1dDUoscm"
            df_bal = pd.read_csv(csv_url)

            # --- Filter matching ledgers ---
            df_bal_filtered = df_bal[df_bal["Ledger Name"].isin(final_ledgers)]

            # --- Clean Closing Balance ---
            df_bal_filtered["Closing Balance"] = df_bal_filtered["Closing Balance"].astype(str)

            def parse_balance(val):
                val = val.replace("Cr", "").replace("Dr", "").replace(",", "").strip()
                try:
                    return float(val)
                except:
                    return 0.0

            df_bal_filtered["BalanceValue"] = df_bal_filtered["Closing Balance"].apply(parse_balance)

            # --- Split into Dr and Cr based on sign ---
            df_dr = df_bal_filtered[df_bal_filtered["BalanceValue"] < 0][["Ledger Name", "Closing Balance"]].reset_index(drop=True)
            df_cr = df_bal_filtered[df_bal_filtered["BalanceValue"] >= 0][["Ledger Name", "Closing Balance"]].reset_index(drop=True)

            # --- Totals ---
            total_cr = df_bal_filtered[df_bal_filtered["BalanceValue"] >= 0]["BalanceValue"].sum()
            total_dr = df_bal_filtered[df_bal_filtered["BalanceValue"] < 0]["BalanceValue"].sum()

            # --- Display in two columns ---
            col1, col2 = st.columns(2, border=True)

            with col1:
                st.markdown("### 💚 Cr. Balance")
                st.dataframe(df_cr)
                st.success(f"**Total Cr: ₹ {total_cr:,.2f}**")

            with col2:
                st.markdown("### 🔴 Dr. Balance (Oustanding)")
                st.dataframe(df_dr)
                st.error(f"**Total Dr: ₹ {abs(total_dr):,.2f}**")

    with tab2:
        st.info("Tab Selected : 📖 Daybook")

        required_columns = {'Date', 'LedgerName', 'Ledger', 'Type', 'VoucherNo', 'DrAmt', 'CrAmt'}
        if required_columns.issubset(df.columns):
            # Convert 'Date' to datetime
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Ledger Type filter (from 'Type' column)
            type_options = sorted(df['Type'].dropna().unique())
            selected_types = st.multiselect("📌 Select Ledger Type(s)", type_options, default=type_options)

            # Date range
            today = datetime.today()
            default_from = today - timedelta(days=1)
            default_to = today

            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input("🗓️ From Date", default_from)
            with col2:
                to_date = st.date_input("🗓️ To Date", default_to)

            st.markdown(f"🗓️ Showing entries from **{from_date.strftime('%d-%m-%y')}** to **{to_date.strftime('%d-%m-%y')}**")

            # Filter data
            filtered_df = df[
                (df['Date'] >= pd.to_datetime(from_date)) &
                (df['Date'] <= pd.to_datetime(to_date)) &
                (df['Type'].isin(selected_types))
            ]

            if not filtered_df.empty:
                # Format date
                filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%y')

                # Reorder columns
                display_cols = ['Date', 'LedgerName', 'Ledger', 'Type', 'VoucherNo', 'DrAmt', 'CrAmt']
                filtered_df = filtered_df[display_cols]

                # Show table
                st.subheader("📄 Daybook Entries")
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)

                # Totals
                total_dr = filtered_df['DrAmt'].sum()
                total_cr = filtered_df['CrAmt'].sum()
                st.success(f"**Total Dr: ₹ {total_dr:,.2f} | Total Cr: ₹ {total_cr:,.2f}**")
            else:
                st.warning("⚠️ No matching entries found.")
        else:
            st.error("❌ Required columns not found. Expected: Date, LedgerName, Ledger, Type, VoucherNo, DrAmt, CrAmt")

    with tab3:
        st.info("Tab Selected : 📘 Ledger & Voucher")
        # UI block for ledger selection

        if 'LedgerName' in df.columns and 'Date' in df.columns:
            # Convert 'Date' column to datetime if not already
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Get unique ledger names
            ledger_options = df['LedgerName'].dropna().unique()
            selected_ledger = st.selectbox("🔍 Select Ledger", sorted(ledger_options),index=None, placeholder="- Select Ledger - ")

            # Default date range: last 2 months
            today = datetime.today()
            default_from_date = today - timedelta(days=60)
            default_to_date = today

            # Date inputs (shown to user)
            col1, col2=st.columns(2)
            with col1:
                from_date = st.date_input("🗓️From Date", default_from_date)
            with col2:
                to_date = st.date_input("🗓️To Date", default_to_date)
            st.markdown(f"🗓️ Showing ledger from **{from_date.strftime('%d-%m-%y')}** to **{to_date.strftime('%d-%m-%y')}**")
            st.divider()

            # Filter dataframe
            filtered_df = df[
                (df['LedgerName'] == selected_ledger) &
                (df['Date'] >= pd.to_datetime(from_date)) &
                (df['Date'] <= pd.to_datetime(to_date))
            ].drop(columns=['LedgerName'])

            # 👉 Format 'Date' for display as dd-mm-yy
            if 'Date' in filtered_df.columns:
                filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%y')

            st.subheader("📑 Ledger Details")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        else:
            st.error("❌ 'LedgerName' or 'Date' column not found in the main ledger data.")

        # Show closing balance
        if 'Ledger Name' in bal_df.columns:
            filtered_bal_df = bal_df[bal_df['Ledger Name'] == selected_ledger]
            if not filtered_bal_df.empty:
                closing_balance = filtered_bal_df['Closing Balance'].values[0]
                st.markdown(f"💰 **Closing Balance**")
                if closing_balance < 0:
                    st.error(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance:,.2f} Dr.")
                else:
                    st.success(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance:,.2f} Cr.")
            else:
                st.warning("No balance information found for the selected ledger.")
        else:
            st.error("❌ 'Ledger Name' column not found in the balance data.")





# ---------------------------------------------------------------Order Page----------------------
def order_page():
    if st.session_state.get("user_role") not in ["Admin", "Standard", "Guest"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white; 
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📦 Order Management
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    tab_new, tab_old = st.tabs(["New Order", "Existing Order"])

    with tab_new:
        username = st.session_state.username

        # --- Distributor Dropdown ---
        st.subheader("Select Distributor")
        distributors = list(dist_collection.find({"assigned_to": username}, {"_id": 0, "name": 1}))
        dist_names = [d["name"] for d in distributors]

        selected_dist = st.selectbox("Distributor Name", dist_names, index=None, placeholder="- Select - ")

        # --- Brand and Type selection ---
        col1, col2 = st.columns(2, border=True)

        with col1:

            st.subheader("Select Device Filters")

            brands = device_collection.distinct("brand")
            selected_brand = st.selectbox("Brand", brands, index=None, placeholder="- Select - ")

            types = device_collection.distinct("type", {"brand": selected_brand})
            selected_type = st.selectbox("Type", types, index=None, placeholder="- Select - ")

            # Filtered model list
            models = device_collection.distinct("model", {"brand": selected_brand, "type": selected_type})
            selected_model = st.selectbox("Model", models, index=None, placeholder="- Select - ")

            qty = st.number_input("Quantity", min_value=0, step=1)

            # Add items to temp session list
            if "order_items" not in st.session_state:
                st.session_state.order_items = []

            if st.button("➕ Add Item", use_container_width=True):
                st.session_state.order_items.append({"model": selected_model, "qty": qty})
                st.success(f"Added {selected_model} x {qty}")

        with col2:
            st.markdown("### 📝 Order Preview")
            if st.session_state.order_items:
                df = pd.DataFrame(st.session_state.order_items)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No items added yet.")
        
        # --- Final Submission ---
        if st.button("✅ Submit Order", use_container_width=True):
            if not st.session_state.order_items:
                st.warning("Please add at least one item to submit the order.")
            else:
                order_doc = {
                    "date": datetime.today(),
                    "status": "New",
                    "order_by": username,
                    "dist_name": selected_dist,
                    "order": st.session_state.order_items
                }
                order_collection.insert_one(order_doc)

                st.success("🟢 Order Submitted Successfully!")
            st.session_state.order_items = []  # clear for next entry

    with tab_old:

        today = datetime.today()
        default_from = today - timedelta(days=30)
        default_to = today

        col1, col2 = st.columns(2, border=True)
        with col1:
            from_date = st.date_input("📅 From Date", value=default_from)
        with col2:
            to_date = st.date_input("📅 To Date", value=default_to)

        # Validate range
        if from_date > to_date:
            st.error("⚠️ 'From Date' cannot be after 'To Date'")
        else:
            # Convert to datetime for MongoDB query
            from_datetime = datetime.combine(from_date, datetime.min.time())
            to_datetime = datetime.combine(to_date, datetime.max.time())

            # MongoDB query
            query = {
                "order_by": username,
                "date": {"$gte": from_datetime, "$lte": to_datetime}
            }

            orders = list(order_collection.find(query).sort("date", -1))

            if not orders:
                st.info("No orders found in selected date range.")
            else:
                st.markdown(f"""
                <div style='
                    display: flex;
                    justify-content: center;
                    background: linear-gradient(180deg, #0a5668, #498fa0);
                    box-shadow: 1px 1px 5px rgba(1, 0, 0,  1.2);
                    margin-top: 0px;
                    margin-bottom: 30px;
                    border-radius: 10px;
                    align-items: center;
                    color : white;
                    padding: 1px;
                '>
                    
                </div> 
            """, unsafe_allow_html=True)
                for order in orders:
                    order_id = str(order["_id"])
                    with st.expander(f"📦 :red[{order['date'].strftime('%Y-%m-%d %H:%M')}] | **:blue[{order['status']}]** | **{order['dist_name']}** "):
                        col_po_left, col_po_right=st.columns(2)
                        with col_po_left:
                            st.markdown(f"**Distributor:** {order['dist_name']}")
                            st.markdown(f"**Status:** **:blue[{order['status']}]**")
                            st.markdown(f"**Date:** {order['date'].strftime('%Y-%m-%d %H:%M')}")
                        with col_po_right:
                            if order['status'] != "New" and order['remarks']: st.badge(f"**⚠️ Remark:** {order['remarks']}", color="red")

                        order_items = order.get("order", [])
                        if order_items:
                            df = pd.DataFrame(order_items)
                            
                            if order['status']=="New":                            
                                modify=st.checkbox("Modify Order",key=f"check_{order_id}")
                                
                                if modify:
                                    tab_modify,tab_add=st.tabs(["Modify","Add"])

                                    with tab_modify:
                                        edited_list=st.data_editor(df, num_rows="dynamic",)


                                        if st.button("Save", use_container_width=True):
                                            if not edited_list.empty:
                                                Updated_order = edited_list.to_dict(orient='records')  # Convert DataFrame to list of dicts
                                                order_collection.update_one(
                                                    {"_id": order["_id"]},
                                                    {"$set": {"order": Updated_order}}
                                                )

                                                st.toast("Order saved !")
                                            else:
                                                st.warning("No data to save.")

                                                
                                            st.rerun()

                                    
                                    with tab_add:
                                        brands = device_collection.distinct("brand")
                                        selected_brand = st.selectbox("Brand", brands   , index=None, placeholder="- Select - ",key=f"Brand_Select_{order_id}")
                                        
                                        types = device_collection.distinct("type", {"brand": selected_brand})
                                        selected_type = st.selectbox("Type", types, index=None, placeholder="- Select - ", key=f"Type_Select_{order_id}")

                                        models = device_collection.distinct("model", {"brand": selected_brand, "type": selected_type})
                                        new_model=st.selectbox("Model", models, index=None, placeholder="- Select - ", key=f"Model_Select_{order_id}")
                                        new_qty=st.number_input("Quantity", min_value=0, step=1, key=f"Qty_Select_{order_id}" )
                                        if st.button("Add", use_container_width=True):
                                            order_collection.update_one(
                                                {"_id": order["_id"]},
                                                {"$push": {"order": {"model": new_model, "qty": new_qty}}}
                                            )
                                            st.toast("Item Added")
                                            
                                            st.rerun()

                                    # with tab_modi:
                                    #     edited_list=st.data_editor(df, num_rows="dynamic") # 👈 Set a key
                                    #     #st.write("Here's the value in Session State:")
                                    #     #st.write(st.session_state["my_key"]) # 👈 Show the value in Session State
                                else:
                                    st.dataframe(df, use_container_width=True)
                            
                            else:
                                st.dataframe(df, use_container_width=True)

                        else:
                            st.warning("No items in this order.")

                        courier_docket_filename = order.get("courier_docket_filename")    
                        if courier_docket_filename:

                            col_doc_left,col_doc_right=st.columns(2)
                            with col_doc_left:
                                st.markdown("**Courier Docket:**")
                            with col_doc_right:
                                if order['status'] != "Delivered": 
                                    mark=st.button("Mark as Delivered", key=f"submit_{order_id}", use_container_width=True)
                                    if mark:
                                        order_collection.update_one(
                                    {"_id": order["_id"]},
                                    {"$set": {
                                        "status": "Delivered",
                                        
                                        
                                    }}
                                )
                                        log_event(f"Update Order : Delivered", f"{username} - {order['date'].strftime('%Y-%m-%d %H:%M')}- {order['dist_name']}")
                                        st.toast("Order updated successfully.")
                                        # Refresh page to reflect change
                                        st.rerun()
                            
                            if order.get("courier_docket_bytes"):
                                file_name = order.get("courier_docket_filename", "docket")

                                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    st.markdown("**📦 Courier Docket Image:**")
                                    st.image(order["courier_docket_bytes"], use_container_width=True)
                                else:
                                    st.markdown("**📎 Courier Docket File:**")
                                    st.download_button(
                                        label=f"Download {file_name}",
                                        data=order["courier_docket_bytes"],
                                        file_name=file_name
                                    )                        

#--------------------------------------------------------------------------------------------

def orders_page():

    if st.session_state.get("user_role") not in ["Guest"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white; 
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📦 Purchase Order
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    username = st.session_state.username

    today = datetime.today()
    default_from = today - timedelta(days=30)
    default_to = today

    col1, col2 = st.columns(2, border=True)
    with col1:
        from_date = st.date_input("📅 From Date", value=default_from)
    with col2:
        to_date = st.date_input("📅 To Date", value=default_to)

    # Validate range
    if from_date > to_date:
        st.error("⚠️ 'From Date' cannot be after 'To Date'")
    else:
        # Convert to datetime for MongoDB query
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        # MongoDB query
        query = {
            "dist_name": username,
            "date": {"$gte": from_datetime, "$lte": to_datetime}
        }

        orders = list(order_collection.find(query).sort("date", -1))

        if not orders:
            st.info("No orders found in selected date range.")
        else:
            st.markdown(f"""
            <div style='
                display: flex;
                justify-content: center;
                background: linear-gradient(180deg, #0a5668, #498fa0);
                box-shadow: 1px 1px 5px rgba(1, 0, 0,  1.2);
                margin-top: 0px;
                margin-bottom: 30px;
                border-radius: 10px;
                align-items: center;
                color : white;
                padding: 1px;
            '>
                
            </div> 
        """, unsafe_allow_html=True)
            for order in orders:
                order_id = str(order["_id"])
                with st.expander(f"📦 :red[{order['date'].strftime('%Y-%m-%d %H:%M')}] | **:blue[{order['status']}]** | Ordered by **:orange[{order['order_by']}]**"):
                    col_po_left, col_po_right=st.columns(2)
                    with col_po_left:
                        st.markdown(f"**Distributor:** {order['dist_name']}")
                        st.markdown(f"**Status:** {order['status']}")
                        st.markdown(f"**Date:** {order['date'].strftime('%Y-%m-%d %H:%M')}")
                    with col_po_right:
                        if order['remarks']: st.badge(f"**⚠️ Remark:** {order['remarks']}", color="red")

                    order_items = order.get("order", [])
                    if order_items:
                        df = pd.DataFrame(order_items)
                        st.dataframe(df, use_container_width=True)

                    else:
                        st.warning("No items in this order.")

                    courier_docket_filename = order.get("courier_docket_filename")    
                    if courier_docket_filename:

                        col_doc_left,col_doc_right=st.columns(2)
                        with col_doc_left:
                            st.markdown("**Courier Docket:**")
                        with col_doc_right:
                            if order['status'] != "Delivered": 
                                mark=st.button("Mark as Delivered", key=f"submit_{order_id}", use_container_width=True)
                                if mark:
                                    order_collection.update_one(
                                {"_id": order["_id"]},
                                {"$set": {
                                    "status": "Delivered",
                                    
                                    
                                }}
                            )
                                    log_event(f"Update Order : Delivered", f"{username} - {order['date'].strftime('%Y-%m-%d %H:%M')}- {order['dist_name']}")
                                    st.toast("Order updated successfully.")
                                    # Refresh page to reflect change
                                    st.rerun()
                        
                        if order.get("courier_docket_bytes"):
                            file_name = order.get("courier_docket_filename", "docket")

                            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                st.markdown("**📦 Courier Docket Image:**")
                                st.image(order["courier_docket_bytes"], use_container_width=True)
                            else:
                                st.markdown("**📎 Courier Docket File:**")
                                st.download_button(
                                    label=f"Download {file_name}",
                                    data=order["courier_docket_bytes"],
                                    file_name=file_name
                                )                        



#-------------------------------------------------------------------------------------------

def manage_order_page():
    if st.session_state.get("user_role") not in ["Admin"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white; 
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📦 Manage Order
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------
    


#-------------------------------------------------------------------------------------------

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
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📱 Devices
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )


        # Form Design CSS
    #--------------------------------------------------------------------
    tab_view, tab_add, tab_add_bulk, tab_delete,tab_delete_all, = st.tabs(["📱Existing Device  ", " ➕Add Device  ", " 📦➕Add Bulk Device.csv   ",  " 🗑️Delete  ", " 📦🗑️Delete All   "])
    with tab_view:
        
        st.subheader("📱 Existing Devices")

        docs = list(device_collection.find())
        user_data = [{**doc, "doc_id": str(doc["_id"])} for doc in docs]

        if user_data:
            df = pd.DataFrame(user_data).drop(columns=["_id"], errors="ignore")
            brand_options = sorted(df["brand"].dropna().unique())
            type_options = sorted(df["type"].dropna().unique())

            col_brand, col_type=st.columns(2,gap="large",border=True)
            with col_brand:
                selected_brands = st.multiselect("Filter by Brand", brand_options, default=brand_options)
            with col_type:
                selected_types = st.multiselect("Filter by Type", type_options, default=type_options)

            filtered_df = df[
                (df["brand"].isin(selected_brands)) &
                (df["type"].isin(selected_types))
            ]
            #st.divider()
            container = st.container(border=True)
           
            column_order = ["brand", "type", "model"]
            ordered_columns = [col for col in column_order if col in filtered_df.columns] + \
                            [col for col in filtered_df.columns if col not in column_order and col != "doc_id"]

            if not filtered_df.empty:
                container.dataframe(filtered_df[ordered_columns])
            else:
                container.info("No devices match the selected filters.")
        else:
            st.info("No Device found.")




    #-------------            



    with tab_add:
        
        docs = list(device_collection.find())
        user_data = [{**doc, "doc_id": str(doc["_id"])} for doc in docs]
        df = pd.DataFrame(user_data)

        col1, col2 = st.columns(2,vertical_alignment="top",gap="small",border=True)
        
        with col1:
            if not df.empty:
                brand_options = sorted(df["brand"].dropna().unique().tolist())
                with st.popover("Add New Brand"):
                    new_brand = st.text_input("Enter New Brand Name", key="new_brand_input").strip().upper()
                    if new_brand:
                        brand_options.append(new_brand)
                        col1.markdown(f"`{new_brand} `: Added in the Brand list")

        with col2:
            if not df.empty:
                type_options = sorted(df["type"].dropna().unique().tolist())
                with st.popover("Add New Type"):
                    new_type = st.text_input("Enter New Type", key="new_type_input").strip().upper()
                    if new_type:
                        type_options.append(new_type)
                        col2.markdown(f"`{new_type} `: Added in the type list")

        with st.form("add_device_form"):
            st.subheader(" ➕ Add Device")
            selected_brand = st.selectbox("Select Brand", brand_options,index=None, placeholder="- Select brand - ") if not df.empty else st.text_input("Enter Brand").strip().upper()
            selected_type = st.selectbox("Select Type", type_options, index=None, placeholder="- Select Type - ") if not df.empty else st.text_input("Enter Type").strip().upper()
            model = st.text_input("Model")

            submitted = st.form_submit_button("Add Device",use_container_width=True)
            if submitted:
                if not selected_brand or not selected_type:
                    st.warning("Please enter both a valid Brand and Type.")
                else:
                    new_device = {
                        "brand": selected_brand,
                        "type": selected_type,
                        "model": model,
                    }
                    device_collection.insert_one(new_device)
                    st.toast("Device added successfully!")
                    st.rerun()

        #----------------
    
    def add_device(data):
        device_collection.insert_one(data)

    with tab_add_bulk:
        st.subheader("📦 Bulk Add Devices")
        col_down, col_up=st.columns(2,gap="large",border=True)
        with col_down:
            st.markdown("**CSV format:** `brand, type, model`")
            template_df = pd.DataFrame(columns=["brand", "type", "model"])
            csv = template_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV Template", csv, "device_template.csv", "text/csv",type="primary")

        with col_up:
            if "bulk_upload_done" not in st.session_state:
                st.session_state.bulk_upload_done = False
            file = st.file_uploader("Upload your CSV", type="csv",)

        if file and not st.session_state.bulk_upload_done:
            try:
                df = pd.read_csv(file)
                required_columns = {"brand", "type", "model"}

                if required_columns.issubset(df.columns):
                    with st.spinner("Adding devices..."):
                        for _, row in df.iterrows():
                            data = row.to_dict()
                            add_device(data)

                    st.success("✅ Devices added successfully.")
                    st.dataframe(df)
                    st.session_state.bulk_upload_done = True
                else:
                    st.error("❌ CSV must have columns: article, brand, type, model, stock")
            except Exception as e:
                st.error(f"❌ Error reading CSV: {e}")

        if st.session_state.bulk_upload_done:
            if st.button("🔄 Upload Another File", use_container_width=True):
                st.session_state.bulk_upload_done = False
#--------------------------------------------
    from bson import ObjectId

    with tab_delete:
        docs = list(device_collection.find())
        user_data = [{**doc, "doc_id": str(doc["_id"])} for doc in docs]
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

            # Final match
            final_df = model_df[model_df["model"] == selected_model]

            if not final_df.empty:
                doc_id = final_df.iloc[0]["doc_id"]
                st.markdown(f"**Ready to delete:** `{selected_brand} | {selected_type} | {selected_model}`")
                if st.button("Delete Device",type="primary", use_container_width=True):
                    device_collection.delete_one({"_id": ObjectId(doc_id)})
                    st.success("Device deleted successfully!")
                    st.rerun()
            else:
                st.warning("Matching device not found.")

#-----------------------------------------------------------------

    def get_unique_values():
        docs = list(device_collection.find())
        brands = sorted(set(doc.get("brand", "") for doc in docs if doc.get("brand")))
        types = sorted(set(doc.get("type", "") for doc in docs if doc.get("type")))
        return brands, types

    def delete_filtered_devices(selected_brands, selected_types):
        query = {}
        if selected_brands:
            query["brand"] = {"$in": selected_brands}
        if selected_types:
            query["type"] = {"$in": selected_types}
        result = device_collection.delete_many(query)
        return result.deleted_count

    with tab_delete_all:
        st.subheader("🗑️ Delete Devices  by Filter")
        brands, types = get_unique_values()
        col1, col2 = st.columns(2)
        with col1:
            selected_brands = st.multiselect("Select Brand(s)", brands)
        with col2:
            selected_types = st.multiselect("Select Type(s)", types)

        st.markdown(f"**Selected brands:** `{', '.join(selected_brands) or 'All'}`")
        st.markdown(f"**Selected types:** `{', '.join(selected_types) or 'All'}`")

        if st.button("🚨 Delete Filtered Devices",type="primary", use_container_width=True):
            with st.spinner("Deleting..."):
                deleted_count = delete_filtered_devices(selected_brands, selected_types)
            st.success(f"✅ Deleted {deleted_count} matching device(s).")
            time.sleep(5)
            st.rerun()
#-------------------------------------------------------------------------------------------------

        
# ---------------------------------------------------------------Logistics Page----------------------
def logistics_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")

    #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            🚚 Logistics
        </h5>
        <br>
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
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            🛠️ Utility
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------
    

# ---------------------------------------------------------------Attendance Page----------------------
def attendance_page():
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            🕒 Attendance
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------
    import re
    import calendar
    from datetime import datetime, date
    from io import BytesIO

    # --------------------
    # Utility: convert gsheet edit/share link -> csv export link
    # --------------------
    def gsheet_to_csv(url: str) -> str:
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", str(url))
        if m:
            return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
        return url

    # --------------------
    # Utility: normalize & load CSV robustly
    # --------------------
    @st.cache_data(show_spinner=False)
    def load_and_normalize(csv_url: str) -> pd.DataFrame:
        df = pd.read_csv(csv_url)
        # strip column names
        df.columns = [c.strip() for c in df.columns]

        # map common names to canonical
        lower_map = {c.lower(): c for c in df.columns}
        def find(colnames):
            for cand in colnames:
                if cand in lower_map:
                    return lower_map[cand]
            return None

        col_no = find(["no", "id", "logno"])
        col_enno = find(["enno", "eno", "employee no", "empid", "emp_id"])
        col_name = find(["name", "employee", "empname"])
        col_datetime = find(["datetime", "date time", "date_time", "date/time", "time"])
        col_date = find(["date"])
        col_in = find(["in", "in_time", "intime"])
        col_out = find(["out", "out_time", "outtime"])

        # Prefer DateTime approach if available
        if col_datetime:
            df["DateTime_raw"] = df[col_datetime].astype(str).str.strip()
            # split
            parts = df["DateTime_raw"].str.split(r"\s+", n=1, expand=True)
            df["date_part"] = parts[0]
            df["time_part"] = parts[1].fillna("")
        else:
            # if separate Date and Time columns exist:
            df["date_part"] = df[col_date].astype(str) if col_date else ""
            # try to derive time from In/Out or Time
            if col_in:
                df["time_part"] = df[col_in].astype(str)
            elif col_out:
                df["time_part"] = df[col_out].astype(str)
            else:
                df["time_part"] = ""

        # helper to fix time strings like "10.16" or "10.16.30" -> "10:16"
        def fix_time_str(t):
            t = str(t).strip()
            if not t or t.lower() in ["nan", "none"]:
                return ""
            # Replace dots between digits with colon (only between digits)
            t2 = re.sub(r"(?<=\d)\.(?=\d)", ":", t)
            # keep only hours:minutes (ignore seconds)
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    return datetime.strptime(t2, fmt).strftime("%H:%M")
                except Exception:
                    pass
            # last resort: try to parse as HH.MM (without replacing)
            t3 = t.replace(".", ":")
            try:
                return datetime.strptime(t3, "%H:%M").strftime("%H:%M")
            except Exception:
                return t2  # return best-effort
        df["Time"] = df["time_part"].apply(fix_time_str)

        # parse date part (day-first)
        def fix_date_str(d):
            try:
                return pd.to_datetime(d, dayfirst=True, errors="coerce")
            except Exception:
                return pd.NaT
        df["Date"] = df["date_part"].apply(fix_date_str)
        df = df.dropna(subset=["Date"])

        # Normalize EnNo and Name
        if col_enno:
            df["EnNo"] = df[col_enno].astype(str).str.strip()
        else:
            # try EnNo from EmpID like columns; fallback to No
            df["EnNo"] = df[col_no].astype(str).str.strip() if col_no else df.index.astype(str)

        if col_name:
            df["Name"] = df[col_name].astype(str).str.strip()
        else:
            df["Name"] = df["EnNo"]

        # Normalize No (log sequence number) which helps pick IN/OUT
        if col_no:
            df["No"] = pd.to_numeric(df[col_no], errors="coerce")
        else:
            df["No"] = pd.NA

        # keep only necessary columns
        return df[["No", "EnNo", "Name", "Date", "Time"]].copy()

    # --------------------
    # UI: get Google Sheet link
    # --------------------
    sheet_input = "https://docs.google.com/spreadsheets/d/1YC97YYG7CSarFgYv1c64TzYPbwZroLFS/edit?usp=sharing"
    csv_url = gsheet_to_csv(sheet_input)

    try:
        raw = load_and_normalize(csv_url)
        st.success("✅ Data loaded.")
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.stop()

    # build month-year choices
    raw["Year"] = raw["Date"].dt.year
    raw["Month"] = raw["Date"].dt.month
    months = sorted(raw[["Year", "Month"]].drop_duplicates().itertuples(index=False, name=None))
    if not months:
        st.warning("No usable dates found in sheet.")
        st.stop()

    # choose month-year
    def label(ym): return f"{calendar.month_name[ym[1]]} {ym[0]}"
    default_idx = len(months) - 1
    sel = st.selectbox("Select Month-Year", options=months, format_func=label, index=default_idx)
    sel_year, sel_month = sel

    # filter raw to selected month
    dfm = raw[(raw["Year"] == sel_year) & (raw["Month"] == sel_month)].copy()
    if dfm.empty:
        st.warning("No records for selected month.")
        st.stop()

    # --------------------
    # Compute In/Out per EnNo,Name,Date (use No if present else Time order)
    # --------------------
    dfm = dfm.sort_values(by=["EnNo", "Name", "Date", "No", "Time"], na_position="last")

    def compute_in_out(g):
        # g is rows for one person on one day
        # prefer to use 'No' if numeric; else rely on Time ordering
        if g["No"].notna().any():
            # pick row with min No and max No
            try:
                in_row = g.loc[g["No"].idxmin()]
                out_row = g.loc[g["No"].idxmax()]
                return pd.Series({"In": in_row["Time"], "Out": out_row["Time"]})
            except Exception:
                pass
        # fallback to first/last by Time
        g_sorted = g.sort_values(by="Time")
        if not g_sorted.empty:
            first = g_sorted.iloc[0]["Time"]
            last = g_sorted.iloc[-1]["Time"]
            return pd.Series({"In": first, "Out": last})
        return pd.Series({"In": "", "Out": ""})

    # group by EnNo, Name, Date (date only)
    grouped = dfm.groupby([dfm["EnNo"], dfm["Name"], dfm["Date"].dt.date], dropna=False)
    daily = grouped.apply(compute_in_out).reset_index()
    daily = daily.rename(columns={0: "tmp"})

    # ensure columns
    daily["In"] = daily["In"].fillna("").astype(str)
    daily["Out"] = daily["Out"].fillna("").astype(str)
    daily["InOut"] = daily["In"] + "\n" + daily["Out"]
    daily["Day"] = pd.to_datetime(daily["Date"]).dt.day

    # --------------------
    # Pivot to report: one row per EnNo|Name ; columns 1..N days
    # --------------------
    month_days = calendar.monthrange(sel_year, sel_month)[1]
    report = daily.pivot_table(index=["EnNo", "Name"], columns="Day", values="InOut", aggfunc="first").fillna("")
    report = report.reset_index()

    # Ensure all day columns exist
    for d in range(1, month_days + 1):
        if d not in report.columns:
            report[d] = ""

    # Order columns
    ordered_cols = ["EnNo", "Name"] + list(range(1, month_days + 1))
    report = report[ordered_cols]

    # Sort by numeric EnNo where possible
    def enno_key(v):
        try:
            return int(v)
        except Exception:
            try:
                return int(str(v))
            except:
                return float("inf")
    report = report.sort_values(by=["EnNo", "Name"], key=lambda col: col.map(lambda v: enno_key(v) if col.name == "EnNo" else v)).reset_index(drop=True)

    # --------------------
    # Summary: DaysPresent, DaysAbsent
    # --------------------
    def count_present(row):
        cnt = 0
        for d in range(1, month_days + 1):
            val = row.get(d, "")
            if isinstance(val, str) and val.strip() != "":
                cnt += 1
        return cnt

    summary = report[["EnNo", "Name"]].copy()
    summary["DaysPresent"] = report.apply(count_present, axis=1)
    summary["DaysAbsent"] = month_days - summary["DaysPresent"]

    # --------------------
    # Display in app
    # --------------------
    st.subheader(f"📊 Detailed Report — {calendar.month_name[sel_month]} {sel_year}")
    st.dataframe(report, use_container_width=True)

    st.subheader("🧾 Summary")
    st.dataframe(summary, use_container_width=True)

    # --------------------
    # Exports: Detailed Excel, Detailed CSV, Summary Excel, Summary CSV
    # --------------------
    def report_to_excel_bytes(df_report: pd.DataFrame, year: int, month: int) -> bytes:
        out = BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            df_report.to_excel(writer, index=False, sheet_name="Detailed")
            workbook = writer.book
            ws = writer.sheets["Detailed"]

            # formats
            wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
            header_fmt = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter"})
            day_fmt = workbook.add_format({"text_wrap": True, "valign": "top"})
            sun_fmt = workbook.add_format({"text_wrap": True, "valign": "top", "bg_color": "#EFEFEF"})

            # widths for EnNo and Name
            ws.set_column(0, 0, 12, wrap)
            ws.set_column(1, 1, 20, wrap)

            # Sunday days list
            sundays = [d for d in range(1, calendar.monthrange(year, month)[1] + 1) if date(year, month, d).weekday() == 6]

            # apply column widths and formats
            for d in range(1, month_days + 1):
                col_idx = 2 + (d - 1)
                if d in sundays:
                    ws.set_column(col_idx, col_idx, 12, sun_fmt)
                else:
                    ws.set_column(col_idx, col_idx, 12, day_fmt)

            # format headers (mark Sunday headers slightly different)
            for col_idx, col_name in enumerate(df_report.columns):
                if isinstance(col_name, int) and col_name in sundays:
                    ws.write(0, col_idx, col_name, workbook.add_format({"bold": True, "bg_color": "#DA8B8B", "align": "center"}))
                else:
                    ws.write(0, col_idx, col_name, header_fmt)

            ws.freeze_panes(1, 2)
            ws.autofilter(0, 0, df_report.shape[0], df_report.shape[1] - 1)
        out.seek(0)
        return out.getvalue()

    def summary_to_excel_bytes(df_summary: pd.DataFrame, year: int, month: int) -> bytes:
        out = BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            df_summary.to_excel(writer, index=False, sheet_name="Summary")
            workbook = writer.book
            worksheet = writer.sheets["Summary"]
            wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
            worksheet.set_column(0, 0, 12, wrap)
            worksheet.set_column(1, 1, 25, wrap)
            worksheet.set_column(2, 3, 12, wrap)
        out.seek(0)
        return out.getvalue()

    # generate bytes
    detailed_excel = report_to_excel_bytes(report, sel_year, sel_month)
    detailed_csv = report.to_csv(index=False).encode("utf-8")
    summary_excel = summary_to_excel_bytes(summary, sel_year, sel_month)
    summary_csv = summary.to_csv(index=False).encode("utf-8")

    # download buttons (separate)
    colA, colB = st.columns(2)
    with colA:
        st.download_button("⬇️ Download Detailed Excel (Sundays shaded)", data=detailed_excel,
                        file_name=f"Attendance_{calendar.month_name[sel_month]}_{sel_year}_Detailed.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with colB:
        st.download_button("⬇️ Download Detailed CSV", data=detailed_csv,
                        file_name=f"Attendance_{calendar.month_name[sel_month]}_{sel_year}_Detailed.csv",
                        mime="text/csv")

    colC, colD = st.columns(2)
    with colC:
        st.download_button("⬇️ Download Summary Excel", data=summary_excel,
                        file_name=f"Attendance_{calendar.month_name[sel_month]}_{sel_year}_Summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with colD:
        st.download_button("⬇️ Download Summary CSV", data=summary_csv,
                        file_name=f"Attendance_{calendar.month_name[sel_month]}_{sel_year}_Summary.csv",
                        mime="text/csv")

    st.caption("Tip: Excel preserves In/Out as two lines in a cell; Streamlit table will show the newline but cell height is limited.")



# ---------------------------------------------------------------Change Password Page----------------------
def Change_Password_page():
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            🔐 Change Password
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    with st.form("Change Password"):
        new_pass=st.text_input("Enter New Password :", type='password')
        confirm_pass=st.text_input("Enter Confirm Password :", type='password')
        submit=st.form_submit_button("Update Password",type="primary",use_container_width=True)
        if new_pass and confirm_pass :
                
                if submit and new_pass==confirm_pass :

                    if st.session_state.user_role == "Guest":
                        dist_collection.update_one({"name": st.session_state.username}, {"$set": {"pwd": confirm_pass}})
                    else:
                        users_collection.update_one({"name": st.session_state.username}, {"$set":{"pass": confirm_pass}})

                    st.success("Password Changed Successfully")

                else:
                    st.error("New Password & Confirm Password Not Matched")


# ---------------------------------------------------------------Update Order Page----------------------
def update_order_page():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📦 Update Order
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------


# CSS for refresh button Color [to be change later]
    st.markdown("""
    <style>
    /*div.stButton > button {
        width: 100%;
        height: 45px;
        font-size: 10px;
        background: linear-gradient(0deg, #062134, #8fc3e7);
        margin-bottom: 5px;
        margin-top: 10px;
        color: white;
        border: none;
        border-radius: 10px;
    }*/

    /* 1-LC [Refresh Button]*/
    .st-emotion-cache-2l7auv.eacrzsi3 {
            background: linear-gradient(0deg, green, lightgreen);
            width: 100%;
            height: auto;
            font-size: 10px;
            margin-bottom: 5px;
            margin-top: 5px;
            color: black;
            border: 10px;
            border-radius: 50px;
            
                }                

    /* 1-LV [Refresh Button] to be update   */
    .st-emotion-cache-2l7auv.eacrzsi3 {
            background: linear-gradient(0deg, green, lightgreen);
            width: 100%;
            height: 100%;
            font-size: 10px;
            margin-bottom: 5px;
            margin-top: 5px;
            color: black;
            border: 10px;
            border-radius: 50px;
            
                }                

                    </style>
""", unsafe_allow_html=True)
    
    username = st.session_state.username    

    col_options, col_refresh=st.columns([8,1])
    with col_refresh:
        # Top-level refresh button
        refresh= st.button("♻️ **Refresh**",type="tertiary", use_container_width=True)
        if refresh:
            st.rerun()
    with col_options:
        options=st.radio("Options: ", ["**:rainbow[Current Orders]**", "**:blue[Order By Date]**"],horizontal=True)
    if options=="**:rainbow[Current Orders]**":
        # Define possible statuses
        status_tabs = ["New", "Billed & Under Approval", "Approved for Dispatch", "Dispached", "Delivered", "Cancelled"]

        # Create tabs for each status
        tabs = st.tabs(status_tabs)

        for idx, status in enumerate(status_tabs):
            with tabs[idx]:
                st.subheader(f"📦 {status} Orders")

                # Fetch orders for user with current status
                orders = list(order_collection.find({
                    "status": status
                }).sort("date", -1))

                if not orders:
                    st.info(f"No '{status}' orders found.")
                else:
                    for order in orders:
                        order_id = str(order["_id"])  # unique ID for each form
                        with st.expander(f"🗓️ {order['date'].strftime('%Y-%m-%d %H:%M')} | **:blue[{order['dist_name']}]**  | Ordered by **:orange[{order['order_by']}]**"):

                            st.markdown(f"**Distributor:** {order['dist_name']}")
                            st.markdown(f"**Date:** {order['date'].strftime('%Y-%m-%d %H:%M')}")
                            st.markdown(f"**Current Status:** **:blue[{order['status']}]**")
                            
                            # Show order items
                            items = order.get("order", [])
                            df = pd.DataFrame(items)
                            
                            modify=st.checkbox("Modify Order",key=f"check_{order_id}")
                            
                            if modify:
                                tab_modify,tab_add=st.tabs(["Modify","Add"])

                                with tab_modify:
                                    edited_list=st.data_editor(df, num_rows="dynamic",)


                                    if st.button("Save", use_container_width=True):
                                        if not edited_list.empty:
                                            Updated_order = edited_list.to_dict(orient='records')  # Convert DataFrame to list of dicts
                                            order_collection.update_one(
                                                {"_id": order["_id"]},
                                                {"$set": {"order": Updated_order}}
                                            )

                                            st.toast("Order saved !")
                                        else:
                                            st.warning("No data to save.")

                                            
                                        st.rerun()

                                
                                with tab_add:
                                    brands = device_collection.distinct("brand")
                                    selected_brand = st.selectbox("Brand", brands   , index=None, placeholder="- Select - ")
                                    
                                    types = device_collection.distinct("type", {"brand": selected_brand})
                                    selected_type = st.selectbox("Type", types, index=None, placeholder="- Select - ")

                                    models = device_collection.distinct("model", {"brand": selected_brand, "type": selected_type})
                                    new_model=st.selectbox("Model", models, index=None, placeholder="- Select - ")
                                    new_qty=st.number_input("Quantity", min_value=0, step=1)
                                    if st.button("Add", use_container_width=True):
                                        order_collection.update_one(
                                            {"_id": order["_id"]},
                                            {"$push": {"order": {"model": new_model, "qty": new_qty}}}
                                        )
                                        st.toast("Item Added")
                                        
                                        st.rerun()

                                # with tab_modi:
                                #     edited_list=st.data_editor(df, num_rows="dynamic") # 👈 Set a key
                                #     #st.write("Here's the value in Session State:")
                                #     #st.write(st.session_state["my_key"]) # 👈 Show the value in Session State
                            else:
                                st.dataframe(df, use_container_width=True)
                            

                            #---------------------------------------------------------------------------------------
                            # shows Docket if available.
                            courier_docket_filename = order.get("courier_docket_filename")
                            if courier_docket_filename:
                                st.markdown("**Courier Docket:**")
                                
                                if order.get("courier_docket_bytes"):
                                    file_name = order.get("courier_docket_filename", "docket")

                                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                        st.markdown("**📦 Courier Docket Image:**")
                                        st.image(order["courier_docket_bytes"], use_container_width=True)
                                    else:
                                        st.markdown("**📎 Courier Docket File:**")
                                        st.download_button(
                                            label=f"Download {file_name}",
                                            data=order["courier_docket_bytes"],
                                            file_name=file_name
                                        )                        

                            # --- Update Form ---
                            st.divider()
                            st.markdown("#### ✏️ Update Order")

                            new_status = st.selectbox(f"Update Status for {order_id}", status_tabs, index=status_tabs.index(status), key=f"status_{order_id}")
                            remarks = st.text_area("Remarks (optional)", key=f"remarks_{order_id}")

                            # --- Upload Docket Image ---
                            docket_file = st.file_uploader("📤 Upload Courier Docket (if dispatched)", type=["jpg", "jpeg", "png", "pdf"], key=f"docket_{order_id}")

                            if docket_file is not None and docket_file.type.startswith("image/"):
                                # Open the uploaded image
                                img = Image.open(docket_file)
                                new_status = "Dispached"
                                # Compress the image
                                compressed_io = io.BytesIO()
                                img.save(compressed_io, format='JPEG', optimize=True, quality=7)  # 5% quality

                                # Get bytes
                                compressed_bytes = compressed_io.getvalue()

                                # Example: Save file info in DB (you can store bytes in GridFS if needed)
                                order_collection.update_one(
                                    {"_id": order["_id"]},
                                    {"$set": {
                                        "courier_docket_filename": docket_file.name,
                                        "courier_docket_uploaded_at": datetime.today(),
                                        "courier_docket_bytes": compressed_bytes,
                                    }}
                                )
                            

                            if st.button("✅ Update", key=f"submit_{order_id}", use_container_width=True):
                                order_collection.update_one(
                                    {"_id": order["_id"]},
                                    {"$set": {
                                        "status": new_status,
                                        "remarks": remarks,
                                        #"order": st.session_state.order_items
                                    }}
                                )
                                log_event(f"Update Order : {new_status}", f"{username} - {order['date'].strftime('%Y-%m-%d %H:%M')}- {order['dist_name']}")
                                st.success("Order updated successfully.")
                                st.rerun()



# ---------------------------------------------------------------Attendance Managment Page----------------------
def att_managment_page():
    if st.session_state.get("user_role") not in ["Admin"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            🕒 Attendance Managment
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    st.write("Attendance Managment page is comming soon")

def ledger_page():
    if st.session_state.get("user_role") not in ["Guest"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        📒 Distributors Ledger Viewer
            </h5>
        <br>
        """,
        unsafe_allow_html=True
    )

    
    # Google Drive file IDs
    file_id = '10NP-jpsSO81Uk_Ms9H_llXmddg6x0xg_'
    bal_file_id = '15wpT8PWvfhTHrefwXxcqWq5j1dDUoscm'

    # Construct direct download URLs
    csv_url = f'https://drive.google.com/uc?id={file_id}'
    bal_csv_url = f'https://drive.google.com/uc?id={bal_file_id}'

    # Load CSVs
    df = pd.read_csv(csv_url)
    bal_df = pd.read_csv(bal_csv_url)

    # UI block for ledger selection

    if 'LedgerName' in df.columns and 'Date' in df.columns:
        # Convert 'Date' column to datetime if not already
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Get unique ledger names
        #st.session_state.username = "Manoj Enterprise Jio Phone"
        selected_ledger = st.session_state.username

        # Default date range: last 2 months
        today = datetime.today()
        default_from_date = today - timedelta(days=60)
        default_to_date = today

        # Date inputs (shown to user)
        col1, col2=st.columns(2)
        with col1:
            from_date = st.date_input("🗓️From Date", default_from_date)
        with col2:
            to_date = st.date_input("🗓️To Date", default_to_date)
        st.markdown(f"🗓️ Showing ledger from **{from_date.strftime('%d-%m-%y')}** to **{to_date.strftime('%d-%m-%y')}**")
        #   st.divider()

        # Filter dataframe
        filtered_df = df[
            (df['LedgerName'] == selected_ledger) &
            (df['Date'] >= pd.to_datetime(from_date)) &
            (df['Date'] <= pd.to_datetime(to_date))
        ].drop(columns=['LedgerName'])

        # 👉 Format 'Date' for display as dd-mm-yy
        if 'Date' in filtered_df.columns:
            filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%y')

        st.subheader(f"📑 _Ledger Details_ : `{st.session_state.username}`")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    else:
        st.error("❌ 'LedgerName' or 'Date' column not found in the main ledger data.")

    # Show closing balance
    if 'Ledger Name' in bal_df.columns:
        filtered_bal_df = bal_df[bal_df['Ledger Name'] == selected_ledger]
        if not filtered_bal_df.empty:
            closing_balance = filtered_bal_df['Closing Balance'].values[0]
            st.markdown(f"💰 **Closing Balance**")
            if closing_balance < 0:
                st.error(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance:,.2f} Dr.")
            else:
                st.success(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance:,.2f} Cr.")
        else:
            st.warning("No balance information found for the selected ledger.")
    else:
        st.error("❌ 'Ledger Name' column not found in the balance data.")


def ledgers_page():
    if st.session_state.get("user_role") not in ["Standard"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
        📒 Distributors Ledger Viewer
            </h5>
        <br>
        """,
        unsafe_allow_html=True
    )

    # Google Drive file IDs
    file_id = '10NP-jpsSO81Uk_Ms9H_llXmddg6x0xg_'
    bal_file_id = '15wpT8PWvfhTHrefwXxcqWq5j1dDUoscm'

    # Construct direct download URLs
    csv_url = f'https://drive.google.com/uc?id={file_id}'
    bal_csv_url = f'https://drive.google.com/uc?id={bal_file_id}'

    # Load CSVs
    df = pd.read_csv(csv_url)
    bal_df = pd.read_csv(bal_csv_url)

    tab1, tab2, tab3=st.tabs(["💰 Ledger Balance", "📖 Daybook", "📘 Ledger & Voucher"])


    with tab1:
        st.info("Tab Selected : 💰 Ledger Balance")

        username = st.session_state.get("username")  # 👈 Get logged-in user
        if not username:
            st.warning("No user logged in.")
        else:
            colb, colc = st.columns(2, border=True)
            with colb:
                # --- UI Filters: Company (Brand) ---
                brand_cursor = dist_collection.find({"assigned_to": username}, {"_id": 0, "brand": 1})
                brand_list = sorted({doc["brand"] for doc in brand_cursor if "brand" in doc and doc["brand"]})
                selected_brand = st.selectbox("Select Brand :", brand_list, index=None, placeholder="- Select brand - ")

            with colc:
                filter_location_check = st.checkbox("Filter location")

                if filter_location_check and selected_brand:
                    location_cursor = dist_collection.find(
                        {"brand": selected_brand, "assigned_to": username},
                        {"_id": 0, "location": 1}
                    )
                    location_list = sorted({doc["location"] for doc in location_cursor if "location" in doc and doc["location"]})
                    selected_location = st.selectbox("Select Location :", location_list, index=None, placeholder="- Select location - ")

                    if selected_location:
                        filtered_ledgers = dist_collection.find(
                            {"brand": selected_brand, "location": selected_location, "assigned_to": username},
                            {"_id": 0, "name": 1}
                        )
                        final_ledgers = [doc["name"] for doc in filtered_ledgers if "name" in doc]
                    else:
                        final_ledgers = []
                else:
                    if selected_brand:
                        filtered_ledgers = dist_collection.find(
                            {"brand": selected_brand, "assigned_to": username},
                            {"_id": 0, "name": 1}
                        )
                        final_ledgers = [doc["name"] for doc in filtered_ledgers if "name" in doc]
                    else:
                        final_ledgers = []

            search_button = st.button("🔍 Search", use_container_width=True)
            if search_button:
                st.divider()
                
                # Load balance data from Drive
                df_bal = pd.read_csv(bal_csv_url)

                # Filter ledgers
                df_bal_filtered = df_bal[df_bal["Ledger Name"].isin(final_ledgers)]
                df_bal_filtered["Closing Balance"] = df_bal_filtered["Closing Balance"].astype(str)

                def parse_balance(val):
                    val = val.replace("Cr", "").replace("Dr", "").replace(",", "").strip()
                    try:
                        return float(val)
                    except:
                        return 0.0

                df_bal_filtered["BalanceValue"] = df_bal_filtered["Closing Balance"].apply(parse_balance)

                # Cr/Dr split
                df_dr = df_bal_filtered[df_bal_filtered["BalanceValue"] < 0][["Ledger Name", "Closing Balance"]].reset_index(drop=True)
                df_cr = df_bal_filtered[df_bal_filtered["BalanceValue"] >= 0][["Ledger Name", "Closing Balance"]].reset_index(drop=True)

                # Totals
                total_cr = df_cr["Closing Balance"].apply(parse_balance).sum()
                total_dr = df_dr["Closing Balance"].apply(parse_balance).sum()

                col1, col2 = st.columns(2, border=True)
                with col1:
                    st.markdown("### 💚 Cr. Balance")
                    st.dataframe(df_cr)
                    st.success(f"**Total Cr: ₹ {total_cr:,.2f}**")

                with col2:
                    st.markdown("### 🔴 Dr. Balance (Outstanding)")
                    st.dataframe(df_dr)
                    st.error(f"**Total Dr: ₹ {abs(total_dr):,.2f}**")

    with tab2:
        st.info("Tab Selected : 📖 Daybook")

        username = st.session_state.get("username")
        if not username:
            st.warning("No user logged in.")
        else:
            # Get ledgers assigned to user
            user_ledgers_cursor = dist_collection.find({"assigned_to": username}, {"_id": 0, "name": 1})
            user_ledgers = sorted({doc["name"] for doc in user_ledgers_cursor if "name" in doc})

            required_columns = {'Date', 'LedgerName', 'Ledger', 'Type', 'VoucherNo', 'DrAmt', 'CrAmt'}
            if required_columns.issubset(df.columns):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

                # Filter by assigned ledgers
                df = df[df["LedgerName"].isin(user_ledgers)]

                type_options = sorted(df['Type'].dropna().unique())
                selected_types = st.multiselect("📌 Select Ledger Type(s)", type_options, default=type_options)

                today = datetime.today()
                default_from = today - timedelta(days=1)
                default_to = today

                col1, col2 = st.columns(2)
                with col1:
                    from_date = st.date_input("🗓️ From Date", default_from)
                with col2:
                    to_date = st.date_input("🗓️ To Date", default_to)

                st.markdown(f"🗓️ Showing entries from **{from_date.strftime('%d-%m-%y')}** to **{to_date.strftime('%d-%m-%y')}**")

                filtered_df = df[
                    (df['Date'] >= pd.to_datetime(from_date)) &
                    (df['Date'] <= pd.to_datetime(to_date)) &
                    (df['Type'].isin(selected_types))
                ]

                if not filtered_df.empty:
                    filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%y')
                    display_cols = ['Date', 'LedgerName', 'Ledger', 'Type', 'VoucherNo', 'DrAmt', 'CrAmt']
                    filtered_df = filtered_df[display_cols]

                    st.subheader("📄 Daybook Entries")
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

                    total_dr = filtered_df['DrAmt'].sum()
                    total_cr = filtered_df['CrAmt'].sum()
                    st.success(f"**Total Dr: ₹ {total_dr:,.2f} | Total Cr: ₹ {total_cr:,.2f}**")
                else:
                    st.warning("⚠️ No matching entries found.")
            else:
                st.error("❌ Required columns not found. Expected: Date, LedgerName, Ledger, Type, VoucherNo, DrAmt, CrAmt")

    with tab3:
        st.info("Tab Selected : 📘 Ledger & Voucher")

        username = st.session_state.get("username")
        if not username:
            st.warning("No user logged in.")
        else:
            # Get ledgers assigned to user
            user_ledgers_cursor = dist_collection.find({"assigned_to": username}, {"_id": 0, "name": 1})
            user_ledgers = sorted({doc["name"] for doc in user_ledgers_cursor if "name" in doc})

            if 'LedgerName' in df.columns and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

                # Filter ledger options by user
                ledger_options = sorted(set(df['LedgerName'].dropna()) & set(user_ledgers))

                selected_ledger = st.selectbox("🔍 Select Ledger", ledger_options, index=None, placeholder="- Select Ledger - ")

                today = datetime.today()
                default_from_date = today - timedelta(days=60)
                default_to_date = today

                col1, col2 = st.columns(2)
                with col1:
                    from_date = st.date_input("🗓️From Date", default_from_date)
                with col2:
                    to_date = st.date_input("🗓️To Date", default_to_date)

                st.markdown(f"🗓️ Showing ledger from **{from_date.strftime('%d-%m-%y')}** to **{to_date.strftime('%d-%m-%y')}**")
                st.divider()

                # Filter dataframe
                filtered_df = df[
                    (df['LedgerName'] == selected_ledger) &
                    (df['Date'] >= pd.to_datetime(from_date)) &
                    (df['Date'] <= pd.to_datetime(to_date))
                ].drop(columns=['LedgerName'])

                # 👉 Format 'Date' for display as dd-mm-yy
                if 'Date' in filtered_df.columns:
                    filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%y')

                st.subheader("📑 Ledger Details")
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)

            else:
                st.error("❌ 'LedgerName' or 'Date' column not found in the main ledger data.")
            # Show closing balance
            if 'Ledger Name' in bal_df.columns:
                filtered_bal_df = bal_df[bal_df['Ledger Name'] == selected_ledger]
                if not filtered_bal_df.empty:
                    closing_balance = filtered_bal_df['Closing Balance'].values[0]
                    st.markdown(f"💰 **Closing Balance**")
                    if closing_balance<0:
                        st.error(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance}")
                    else:
                        st.success(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance}")
                else:
                    st.warning("No balance information found for the selected ledger.")
            else:
                st.error("❌ 'Ledger Name' column not found in the balance data.")


def logs():

    st.write("`Logs` :")
    logs = list(log_collection.find().sort("timestamp", -1))
    
    if logs:
        # Optional: remove MongoDB's ObjectId for cleaner display
        for log in logs:
            log.pop('_id', None)
        
        # Convert to DataFrame
        df_logs = pd.DataFrame(logs)

        # Show in Streamlit
        st.dataframe(df_logs)
    else:
        st.info("No logs found")

 # Delete all logs with confirmation
    if st.checkbox("⚠️ I want to delete all logs"):
        if st.button("🗑️ Confirm Delete All Logs", type="primary", use_container_width=True):
            log_collection.delete_many({})
            st.success("All logs have been deleted.")
            st.rerun()


def assign_user_page ():
    if st.session_state.get("user_role") not in ["Admin", "Back Office"]:
        st.error("Access denied.")
        #---------------------- individual page title------------------
    st.markdown(
        """
        <h5 style='
        background-color:#125078; 
        padding:10px; 
        border-radius:10px; 
        color:white;
        box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
        text-align: center;'>
            📦 Assign User with Distributor 
        </h5>
        <br>
        """,
        unsafe_allow_html=True
    )
    #--------------------------------------------------------------------

    user_list=users_collection.find({"type": "Standard"}, {"name": 1, "_id": 0})
    selected_user=st.selectbox("Select User : ",user_list, index=None, placeholder="-Select User-")

    col_unassigned, col_assigned=st.columns(2,border=True)
    with col_unassigned:
        filter=st.checkbox("Filter")
        if filter:
            
            brands=dist_collection.distinct("brand")
            selected_brand = st.selectbox("Brand", brands, index=None, placeholder="- Select - ")

            location=dist_collection.distinct("location", {"brand": selected_brand})
            selected_location=st.selectbox("Select Location", location, index=None, placeholder="-Select-")

            unassigned_list=list(dist_collection.find({"brand":selected_brand, "location":selected_location},{"name": 1, "_id": 0}))
            
            if unassigned_list:
                st.badge("Filtered List:", icon=":material/check:", color="blue")
        else:
            unassigned_list=list(dist_collection.find({},{"name": 1, "_id": 0}))
        
        if unassigned_list:
            modified_list=st.data_editor(unassigned_list, num_rows="dynamic", key="unassigned")

        # ✅ Step 1: Fix existing non-array 'assigned_to' fields
        dist_collection.update_many(
            {"assigned_to": {"$exists": True, "$not": {"$type": "array"}}},
            [{"$set": {"assigned_to": ["$assigned_to"]}}]  # Wrap existing value in a list
        )

        add_to_list=st.button(f" Assign List to {selected_user} ➡️")
                
        if add_to_list and modified_list and selected_user:
            # Extract names from the modified list
            name_list = [item["name"] for item in modified_list if "name" in item]
            
            # Perform the update
            dist_collection.update_many(
                {"name": {"$in": name_list}},
                {"$addToSet": {"assigned_to": selected_user}}
            )
            st.toast(f"User :blue[{selected_user}] :green[Assigned] to selected Distributor")


    with col_assigned:
        st.write(f"Existing Distributors assined to :blue[{selected_user}]")
        assigned_list=list(dist_collection.find({"assigned_to":selected_user},{"name": 1, "_id": 0}))
        st.dataframe(assigned_list)
        clear_btn=st.button(f"🗑️Clear Existing List of {selected_user}")
        if clear_btn and selected_user:
            dist_collection.update_many(
                {},  # match all distributors
                {"$pull": {"assigned_to": selected_user}}
            )
            st.toast(f"User ':blue[{selected_user}]' :red[removed] from all distributors.")
            st.rerun()


# -------------------------------
# 🚀 MAIN APP
# -------------------------------
def main():
    # Inject CSS to hide Streamlit UI elements
    hide_streamlit_style = """
        <style>
        /* Hide top-right hamburger menu and fullscreen option */
        /*#MainMenu {visibility: hidden;}*/
        footer {visibility: hidden;}
        /*header {visibility: hidden;}*/
        

        /* Hide bottom-right Streamlit branding */
        .stDeployButton {display: none;}
        .st-emotion-cache-zq5wmm {display: none;}  /* Updated Streamlit version class for deploy button */
        ._link_gzau3_10 {{display: none;}}
        [data-testid="appCreatorAvatar"] {display: none;}
        [data-testid="stBaseButton-header"] {display: none;}
        .st-emotion-cache-qt4i0q {{display: none;}}
        .st-emotion-cache-usvq0g {{display: none;}}
        /* Optional: Hide top status bar completely */
        .st-emotion-cache-1dp5vir.ezrtsby0 {display: none;}
        ._profilePreview_gzau3_63 {{display: none;}}
        ._link_gzau3_10 {{display: none;}}
        
        
        
        
        </style>
    """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    

    if not st.session_state.get("logged_in"):

        



        app_img_path = "back.jpg"
        app_img_base64 = get_base64(app_img_path)

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

        if not st.session_state.logged_in:
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{app_img_base64}");
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    color: black
                    
                }}

                /* To make header part transparent*/            
                [data-testid="stHeader"]{{
                    
                    background-color: rgba(0,0,0,0);

                }}

                /* To make form design*/ 
                [data-testid="stForm"] {{
                    background: linear-gradient(135deg, lightBlue, white);
                    
                    padding: 30px;
                    border-radius: 30px;
                    box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
                    max-width: 500px;
                    margin: 0 auto;
                    color: Black;
                }}

                
                /* Input fields, text, and labels */
                label, input, textarea, .stTextInput, .stPassword, .stRadio label {{
                    color: black !important;
                }}

                /* Radio button fixes */
                .stRadio label, .stRadio div, div[role="radiogroup"] label, div[role="radiogroup"] > div {{
                    color: black !important;
                }}

                /* To make button Redesign*/            
                [data-testid="stBaseButton-secondaryFormSubmit"]{{
                    margin: 0 auto;
                    display: block; /* to set button @ Center*/
                    background: linear-gradient(10deg, lightgreen, white);
                    box-shadow: 4px 4px 12px rgba(1, 0, 0, 1.2);
                    padding: 8px 16px;
                    margin-top: 20px;
                    border-radius: 50px;
                    width: 50%;
                    padding: 15px;

                       

                }}
                
                [data-testid="stTextInputRootElement"]{{
                    margin: 0 auto;
                    background: linear-gradient(10deg, white, white);
                    box-shadow: 4px 4px 12px rgba(1, 0, 0, .5);
                }}

                
                /* Optional: light background for inputs */
                input {{
                    background-color: rgba(255, 255, 255, 0.85) !important;
                }}
                /* Optional: make input field background semi-transparent white */
                input {{
                    background-color: rgba(255, 255, 255, 0.8) !important;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

            login()
            return
        else:
            st.write("test")
            st.markdown(
            """
            <style>
            .stApp {
                background: none !important;
                
            }

            </style>
            """,
            unsafe_allow_html=True
            )


    # set default page
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    
    show_sidebar()

    page = st.session_state.selected_page
    if page == "Home":
        home_page()
    elif page == "Users":
        log_event("USER PAGE", st.session_state.username)
        users_page()
    elif page == "Distributors":
        log_event("distributors_page", st.session_state.username)
        distributors_page()
    elif page == "Order":
        log_event("order_page", st.session_state.username)
        order_page()
    elif page == "Logistics":
        log_event("logistics_page", st.session_state.username)
        logistics_page()
    elif page == "Utility":
        log_event("utility_page", st.session_state.username)
        utility_page()
    elif page == "Attendance":
        log_event("attendance_page", st.session_state.username)
        attendance_page()
    elif page == "Change_Password":
        log_event("Change_Password_page", st.session_state.username)
        Change_Password_page()
    elif page == "Update Order":
        # log_event("update_order_page", st.session_state.username)
        update_order_page()
    elif page == "Attendance Managment":
        log_event("att_managment_page", st.session_state.username)
        att_managment_page()
    elif page == "Devices":
        log_event("devices_page", st.session_state.username)
        devices_page()
    elif page == "Distributors Ledgers":
        log_event("distributors_ledgers_page", st.session_state.username)
        distributors_ledgers_page()
    elif page == "Ledger":
        log_event("ledger_page", st.session_state.username)
        ledger_page()
    elif page == "Ledgers":
        log_event("ledgers_page", st.session_state.username)
        ledgers_page()
    elif page == "Logs":
        log_event("logs", st.session_state.username)
        logs()
    elif page == "Orders":
        log_event("orders", st.session_state.username)
        orders_page()
    elif page == "Manage Order":
        log_event("Manage Order", st.session_state.username)
        manage_order_page()
    elif page == "Assign User":
        log_event("Assign User", st.session_state.username)
        assign_user_page()
    
    
    
    
    





if __name__ == "__main__":
    main()
