import streamlit as st
import sqlite3
import pandas as pd
st.cache_data.clear()

st.set_page_config(
    page_title="User Manager App",
    page_icon="/workspaces/blank-app/BJ LOGO 2.jpg",
    layout="centered"
)
st.title("👋 Welcome to the User Manager App")

# --- Connect to DB ---
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

# --- Create users table if not exists ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    pass TEXT
)
""")

# --- Create models table if not exists ---
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

if "page" not in st.session_state:
    st.session_state.page = None

# --- Login Form ---
if not st.session_state.logged_in:
    st.subheader("Please Login")
    with st.form("login_form"):
        name = st.text_input("Enter User Name: ").strip().upper()
        password = st.text_input("Enter Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            cursor.execute("SELECT * FROM users WHERE name = ? AND pass = ?", (name, password))
            user = cursor.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_type = user[2]
                st.success(f"Welcome {name}! You are logged in as {user[2]}.")
                st.rerun()
            else:
                st.error("Invalid credentials, please try again.")

# --- Logged In Navigation ---
if st.session_state.logged_in:
    st.sidebar.image("/workspaces/blank-app/BJ LOGO 2.jpg", use_container_width=True)
    st.sidebar.title("Navigation")

    # Navigation for different roles
    if st.session_state.user_type == "Admin":
        st.session_state.page = st.sidebar.radio("Choose page", ["View Users", "Add User", "Delete User", "Add Model"])
    elif st.session_state.user_type in ["Standard", "Guest"]:
        st.session_state.page = st.sidebar.radio("Choose page", ["View Users"])

    # --- Page: Add User ---
    if st.session_state.page == "Add User" and st.session_state.user_type == "Admin":
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
            st.download_button(
                label="📥 Download CSV Format",
                data=f,
                file_name="add-bulk.csv",
                mime="text/csv"
            )

        st.subheader("📂 Upload CSV to Add Users in Bulk")
        csv_file = st.file_uploader("Upload a CSV file with columns: name, type, pass", type="csv")

        if csv_file and "processed_bulk_upload" not in st.session_state:
            try:
                df = pd.read_csv(csv_file)
                required_cols = {"name", "type", "pass"}
                if not required_cols.issubset(df.columns.str.lower()):
                    st.error(f"CSV must include the following columns: {', '.join(required_cols)}")
                else:
                    df.columns = df.columns.str.lower()
                    df["name"] = df["name"].str.strip().str.upper()
                    for _, row in df.iterrows():
                        cursor.execute("INSERT INTO users (name, type, pass) VALUES (?, ?, ?)",
                                    (row["name"], row["type"], row["pass"]))
                    conn.commit()
                    st.success(f"{len(df)} users added successfully!")
                    st.session_state.processed_bulk_upload = True  # Mark this as processed
            except Exception as e:
                st.error(f"Error processing file: {e}")

    # --- Page: View Users ---
    elif st.session_state.page == "View Users":
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)

    # --- Page: Delete User ---
    elif st.session_state.page == "Delete User" and st.session_state.user_type == "Admin":
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
        # Reset Models Table button with confirmation

        confirm_reset = st.checkbox("Are you sure you want to delete all Users?")
        if st.button("Reset All Users Data"):
            
            if confirm_reset:
                cursor.execute("DELETE FROM users")
                conn.commit()
                st.success("All models have been deleted.")
                st.rerun()  # Refresh the app after deletion
            else:
                st.info("Please check the box to confirm before resetting the Users.", icon="⚠️")       

    # --- Page: Add Model ---
    elif st.session_state.page == "Add Model" and st.session_state.user_type == "Admin":
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

        st.markdown("---")

        # Download template
        model_template = pd.DataFrame(columns=["model", "color", "specs"])
        st.download_button("📥 Download Model CSV Template", model_template.to_csv(index=False).encode(), "model-template.csv", "text/csv")

        # Bulk Upload
        st.subheader("📂 Upload CSV to Add Models in Bulk")
        csv_model_file = st.file_uploader("Upload CSV with columns: model, color, specs", type="csv")

        if csv_model_file and "processed_bulk_upload_models" not in st.session_state:
            try:
                df = pd.read_csv(csv_model_file)
                required_cols = {"model", "color", "specs"}
                if not required_cols.issubset(df.columns.str.lower()):
                    st.error("CSV must include columns: model, color, specs")
                else:
                    df.columns = df.columns.str.lower()
                    for _, row in df.iterrows():
                        cursor.execute("INSERT INTO models (model, color, specs) VALUES (?, ?, ?)",
                                    (row["model"], row["color"], row["specs"]))
                    conn.commit()
                    st.success(f"{len(df)} models added successfully!")
                    st.session_state.processed_bulk_upload_models = True  # Mark as processed
            except Exception as e:
                st.error(f"Error uploading models: {e}")

        # --- Delete Model Option ---
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
                cursor.execute("""
                    DELETE FROM models
                    WHERE model = ? AND color = ? AND specs = ?
                """, (selected_model, selected_color, selected_specs))
                conn.commit()
                st.success(f"Deleted model: {selected_model} / {selected_color}")
                st.rerun()

        # Reset Models Table button with confirmation
        confirm_reset = st.checkbox("Are you sure you want to delete all models?")
        if st.button("Reset Models Table"):
            
            if confirm_reset:
                cursor.execute("DELETE FROM models")
                conn.commit()
                st.success("All models have been deleted.")
                st.rerun()  # Refresh the app after deletion
            else:
                st.info("Please check the box to confirm before resetting the models.", icon="⚠️")       
     

# --- Close connection ---
conn.close()
