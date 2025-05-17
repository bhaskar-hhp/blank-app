import streamlit as st

# Initialize selected_page if not already set
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

# Sidebar buttons
st.sidebar.title("📂 Navigation")

if st.sidebar.button("🏠 Home"):
    st.session_state.selected_page = "Home"

if st.sidebar.button("📝 Form"):
    st.session_state.selected_page = "Form"

if st.sidebar.button("📊 Reports"):
    st.session_state.selected_page = "Reports"

# Display content based on selected_page
page = st.session_state.selected_page

if page == "Home":
    st.title("🏠 Home Page")
    st.write("Welcome to the homepage.")

elif page == "Form":
    st.title("📝 Form Page")
    name = st.text_input("Enter your name")
    if st.button("Submit"):
        st.success(f"Hello, {name}!")

elif page == "Reports":
    st.title("📊 Reports")
    st.write("This is where reports will appear.")
