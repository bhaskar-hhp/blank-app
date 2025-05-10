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

st.subheader("User Table")
df = pd.read_sql_query("SELECT * FROM users", conn)
st.dataframe(df, use_container_width=True)

st.dataframe(df.style.highlight_max(axis=0))

st.table(df)

st.bar_chart(df.set_index('name')['age'])

