# pages/view_users.py

import streamlit as st
import sqlite3
import pandas as pd

def show():
    conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
    st.title("All Users")
    df = pd.read_sql_query("SELECT * FROM users", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
