import streamlit as st

# Set up session state to track the active button
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# Function to update state
def set_active(page):
    st.session_state.active_page = page

# Sidebar layout with custom active style
st.sidebar.markdown(
    """
    <style>

    /* Hide top-right hamburger menu and fullscreen option */
    /*#MainMenu {visibility: hidden;}*/
    footer {visibility: hidden;}
    /*header {visibility: hidden;}*/
    

    /* Hide bottom-right Streamlit branding */
    .stDeployButton {display: none;}
    .st-emotion-cache-zq5wmm {display: none;}  /* Updated Streamlit version class for deploy button */
    ._link_gzau3_10 {{display: none;}}
    [data-testid="appCreatorAvatar"]{display: none;}

    /* Optional: Hide top status bar completely */
    .st-emotion-cache-1dp5vir.ezrtsby0 {display: none;}
        

    .sidebar-button {
        padding: 10px 16px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
        font-weight: bold;
    }
    .active {
        background-color: #00bfff;
        color: white;
    }
    .inactive {
        background-color: transparent;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar buttons using markdown (mimicking buttons)
for page in ["Home", "Orders", "Settings"]:
    active_class = "active" if st.session_state.active_page == page else "inactive"
    if st.sidebar.button(f"{page}", key=page, on_click=set_active, args=(page,)):
        pass
    st.sidebar.markdown(f"<div class='sidebar-button {active_class}'>{page}</div>", unsafe_allow_html=True)

# Show content for the active page
st.markdown(f"### You are viewing: {st.session_state.active_page}")
