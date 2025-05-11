import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Home", page_icon="🏠")
st.title("🏠 Home Dashboard")

# --- Connect to DB ---
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

# --- Ensure logged in ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

# --- Main Content ---
st.subheader("Welcome to the Model Management App!")
st.markdown("""
Use the sidebar to navigate between:

- ➕ **Add Model** to input new models
- 📋 **View Existing Models**
- 🗑️ **Delete Models**
""")

# --- Optionally show summary info ---
model_count = cursor.execute("SELECT COUNT(*) FROM models").fetchone()[0]
st.metric("📊 Total Models", model_count)

# --- Close connection ---
conn.close()
