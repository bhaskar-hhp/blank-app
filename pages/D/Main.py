import streamlit as st
from login_page import show_login

st.set_page_config(page_title="Swiftcom DMS", page_icon="🔐")


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



if "authenticated" not in st.session_state or not st.session_state.authenticated:
    if show_login():
        st.rerun()  # rerun to show nav once logged in
else:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    


    # User is authenticated; show navigation
    page_2 = st.Page("page1.py", title="Model", icon="❄️")
    page_3 = st.Page("page2.py", title="User", icon="🎉")

    st.sidebar.title("Navigation")
  
    pg = st.navigation([page_2, page_3])
    
    pg.run()
