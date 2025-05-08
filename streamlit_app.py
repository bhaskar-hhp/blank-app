import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite DB (or create if it doesn't exist)
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Create a sample table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT
)
""")
conn.commit()

in_name = st.text_input("Enter Your Name: ")
in_age = st.selectbox("Enter Your Class: ",("1 - 20","21 - 40","41 - 60","61 - 100"))

button = st.button("Done")
if button :
    st.markdown(f""" 
    Name : {in_name}
    \nAge : {in_age}

    """)

with st.form("entry_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)
    submitted = st.form_submit_button("Add User")

    if submitted:
        cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        st.success("User added!")

# Display data
st.subheader("User List")
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    st.write(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
