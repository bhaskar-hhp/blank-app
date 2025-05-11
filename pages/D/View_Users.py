# pages/view_users.py

import streamlit as st
import sqlite3
import pandas as pd

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

def show():
    conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
    st.title("All Users")
    df = pd.read_sql_query("SELECT * FROM users", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
