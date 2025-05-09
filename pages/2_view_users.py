import streamlit as st
import sqlite3
import pandas as pd

st.title("View All Users")

conn = sqlite3.connect("data.db", check_same_thread=False)

df = pd.read_sql_query("SELECT * FROM users", conn)

if df.empty:
    st.info("No users found.")
else:
    st.dataframe(df, use_container_width=True)


