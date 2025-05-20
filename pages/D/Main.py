import streamlit as st

# Define the pages
main_page = st.Page("main_page.py", title="Main Page", icon="🎈")
page_2 = st.Page("Add_Model.py", title="Add Model", icon="❄️")
page_3 = st.Page("Add_User.py", title="Add User", icon="🎉")

# Set up navigation
pg = st.navigation([main_page, Add_Model, Add_User])

# Run the selected page
pg.run()
