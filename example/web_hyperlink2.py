import streamlit as st

st.title("Open Link in New Tab")

url = "https://www.google.com"

# Create an HTML button that opens the URL in a new tab
st.markdown(f"""
    <form action="{url}" target="_blank">
        <input type="submit" value="Open Workspace" />
    </form>
""", unsafe_allow_html=True)
