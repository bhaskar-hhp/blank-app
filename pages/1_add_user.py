import streamlit as st
import sqlite3

st.title("Add a New User")
st.write("Enter the details of the new user below:")

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
)
""")
conn.commit()

with st.form("add_user_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)
    submitted = st.form_submit_button("Add")
    if submitted:
        cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        st.success(f"User '{name}' added!")

