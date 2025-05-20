import streamlit as st
from login_page import show_login


st.set_page_config(page_title="Secure App", page_icon="🔐")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    if show_login():
        st.rerun()  # rerun to show nav once logged in
else:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    # User is authenticated; show navigation
    page_2 = st.Page("Add_Model.py", title="Model", icon="❄️")
    page_3 = st.Page("Add_User.py", title="User", icon="🎉")

    pg = st.navigation([page_2, page_3])
    pg.run()
