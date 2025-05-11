import streamlit as st
import sqlite3
import pandas as pd

# --- Clear cached data ---
st.cache_data.clear()

# --- Page config ---
st.set_page_config(page_title="Model Manager", page_icon="🛠️")

# --- Connect to DB ---
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

# --- Create tables if not exist ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    pass TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT,
    color TEXT,
    specs TEXT
)
""")
conn.commit()

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "usertype" not in st.session_state:
    st.session_state.usertype = ""
if "page" not in st.session_state:
    st.session_state.page = None

# --- Login section ---
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute("SELECT * FROM users WHERE name = ? AND pass = ?", (username.strip().upper(), password))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.usertype = user[2]
            st.success(f"Welcome {user[1]}! You are logged in as {user[2]}.")
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")

# --- After login ---
if st.session_state.logged_in:
    st.sidebar.image("/workspaces/blank-app/logo.png", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.usertype})")

    if st.session_state.usertype == "Admin":
        st.session_state.page = st.sidebar.radio("Choose page", ["View Users", "Add User", "Delete User", "Add Model"])
    else:
        st.session_state.page = "Home"

    # --- Logout ---
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "username", "usertype", "page"]:
            st.session_state.pop(key, None)
        st.rerun()

    # --- Pages ---
    if st.session_state.page == "View Users":
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)

    elif st.session_state.page == "Add User":
        st.title("Add New User")
        with st.form("add_form"):
            name = st.text_input("Enter User Name: ").strip().upper()
            user_type = st.selectbox("User Type", ["Admin", "Standard", "Guest"])
            password = st.text_input("Create Password", type="password")
            submit = st.form_submit_button("Add")

            if submit:
                if not name or not password:
                    st.warning("Please provide both a name and a password.")
                else:
                    cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)", (name, user_type, password))
                    conn.commit()
                    st.success(f"User '{name}' added!")
                    st.rerun()

        st.markdown("---")
        with open("add-bulk.csv", "rb") as f:
            st.download_button("📥 Download CSV Format", data=f, file_name="add-bulk.csv", mime="text/csv")

        st.subheader("📂 Upload CSV to Add Users in Bulk")
        csv_file = st.file_uploader("Upload a CSV file with columns: name, type, pass", type="csv")

        if csv_file and "processed_bulk_upload" not in st.session_state:
            try:
                df = pd.read_csv(csv_file)
                df.columns = df.columns.str.lower()
                df["name"] = df["name"].str.strip().str.upper()
                for _, row in df.iterrows():
                    cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)",
                                (row["name"], row["type"], row["pass"]))
                conn.commit()
                st.success(f"{len(df)} users added successfully!")
                st.session_state.processed_bulk_upload = True
            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif st.session_state.page == "Delete User":
        st.title("Delete a User")
        df = pd.read_sql_query("SELECT * FROM users", conn)

        if df.empty:
            st.info("No users found.")
        else:
            st.dataframe(df)
            selected_id = st.radio("Select User ID to Delete", df["id"])
            selected_user = df[df["id"] == selected_id]
            st.write("Selected User:")
            st.table(selected_user)

            if st.button("Delete"):
                cursor.execute("DELETE FROM users WHERE id = ?", (selected_id,))
                conn.commit()
                st.success(f"User with ID {selected_id} deleted.")
                st.rerun()

        confirm_reset = st.checkbox("Are you sure you want to delete all Users?")
        if st.button("Reset All Users Data"):
            if confirm_reset:
                cursor.execute("DELETE FROM users")
                conn.commit()
                st.success("All users have been deleted.")
                st.rerun()
            else:
                st.info("Please check the box to confirm before resetting the Users.", icon="⚠️")

    elif st.session_state.page == "Add Model":
        st.title("📋 Existing Models")
        df_models = pd.read_sql_query("SELECT * FROM models", conn)
        if df_models.empty:
            st.info("No models added yet.")
        else:
            st.dataframe(df_models, use_container_width=True)

        st.markdown("---")
        st.title("➕ Add New Model")

        with st.form("add_model_form"):
            model = st.text_input("Model Name")
            color = st.text_input("Color")
            specs = st.text_area("Specifications")
            submit = st.form_submit_button("Add Model")

            if submit:
                if not model or not color or not specs:
                    st.warning("Please fill in all fields.")
                else:
                    cursor.execute("INSERT INTO models (model, color, specs) VALUES (?, ?, ?)", (model, color, specs))
                    conn.commit()
                    st.success(f"Model '{model}' added successfully!")
                    st.rerun()

        model_template = pd.DataFrame(columns=["model", "color", "specs"])
        st.download_button("📥 Download Model CSV Template", model_template.to_csv(index=False).encode(), "model-template.csv", "text/csv")

        st.subheader("📂 Upload CSV to Add Models in Bulk")
        csv_model_file = st.file_uploader("Upload CSV with columns: model, color, specs", type="csv")

        if csv_model_file and "processed_bulk_upload_models" not in st.session_state:
            try:
                df = pd.read_csv(csv_model_file)
                df.columns = df.columns.str.lower()
                for _, row in df.iterrows():
                    cursor.execute("INSERT INTO models (model, color, specs) VALUES (?, ?, ?)",
                                (row["model"], row["color"], row["specs"]))
                conn.commit()
                st.success(f"{len(df)} models added successfully!")
                st.session_state.processed_bulk_upload_models = True
            except Exception as e:
                st.error(f"Error uploading models: {e}")

        st.markdown("---")
        st.subheader("🗑️ Delete a Model Entry")

        if df_models.empty:
            st.info("No model data available to delete.")
        else:
            selected_model = st.selectbox("Select Model", df_models["model"].unique())
            filtered_by_model = df_models[df_models["model"] == selected_model]

            selected_color = st.selectbox("Select Color", filtered_by_model["color"].unique())
            filtered_by_color = filtered_by_model[filtered_by_model["color"] == selected_color]

            selected_specs = st.selectbox("Select Specifications", filtered_by_color["specs"].unique())

            if st.button("Delete Selected Model Entry"):
                cursor.execute("DELETE FROM models WHERE model = ? AND color = ? AND specs = ?",
                            (selected_model, selected_color, selected_specs))
                conn.commit()
                st.success(f"Deleted model: {selected_model} / {selected_color}")
                st.rerun()

        confirm_reset = st.checkbox("Are you sure you want to delete all models?")
        if st.button("Reset Models Table"):
            if confirm_reset:
                cursor.execute("DELETE FROM models")
                conn.commit()
                st.success("All models have been deleted.")
                st.rerun()
            else:
                st.info("Please check the box to confirm before resetting the models.", icon="⚠️")

    else:
        st.title("🏠 Home")
        st.write("Welcome to the Model Manager dashboard.")

# --- Close DB connection ---
conn.close()
