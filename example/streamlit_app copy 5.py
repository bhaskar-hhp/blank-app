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
    brand TEXT,
    model TEXT,
    color TEXT,
    specs TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    location TEXT,
    contact TEXT,
    email TEXT,
    added_by TEXT
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
        st.session_state.page = st.sidebar.radio(
            "Choose page",
            [
                "📦 Dashboard", 
                "👤 Add User", 
                "🗑️ Delete User", 
                "➕ Add/Delete Model", 
                "🏪 Add/Delete Distributor"
            ]        )
    else:
        st.session_state.page = "Home"

    # --- Logout ---
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "username", "usertype", "page"]:
            st.session_state.pop(key, None)
        st.rerun()

    # --- Pages ---

    # View Users
    if st.session_state.page == "📦 Dashboard":
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)

        st.title("All Distributors")
        df = pd.read_sql_query("SELECT * FROM dist", conn)
        st.dataframe(df, use_container_width=True)

        st.title("All Models")
        df = pd.read_sql_query("SELECT * FROM models", conn)
        st.dataframe(df, use_container_width=True)
 
    # add user
    elif st.session_state.page == "👤 Add User":
        st.title("All Users")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df, use_container_width=True)
        st.title("Add New User")
        with st.form("add_form"):
            name = st.text_input("Enter User Name: ").strip().upper()
            user_type = st.selectbox("User Type", ["Admin", "Standard", "Guest", "Back Office"])
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
    ## delete user
    elif st.session_state.page == "🗑️ Delete User":
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
    
    #add model
    elif st.session_state.page == "➕ Add/Delete Model":
        st.title("📋 Existing Models")
        df_models = pd.read_sql_query("SELECT * FROM models", conn)
        if df_models.empty:
            st.info("No models added yet.")
        else:
            st.dataframe(df_models, use_container_width=True)

        st.markdown("---")
        st.title("➕ Add New Model")

        # Add model form
        with st.form("add_model_form"):
            all_brands = df_models["brand"].unique().tolist()
            custom_brand = st.text_input("Or type a new brand (If Brand not in list)")
            selected_brand = st.selectbox("Select a brand", all_brands)

            brand = custom_brand if custom_brand else selected_brand
            model = st.text_input("Model Name")
            color = st.text_input("Color")
            specs = st.text_area("Specifications")
            submit = st.form_submit_button("Add Model")

            if submit:
                if not brand or not model or not color or not specs:
                    st.warning("Please fill in all fields.")
                else:
                    cursor.execute("INSERT INTO models (brand, model, color, specs) VALUES (?, ?, ?, ?)", (brand, model, color, specs))
                    conn.commit()
                    st.success(f"Model '{model}' added successfully!")
                    st.rerun()
        # Download CSV template
        model_template = pd.DataFrame(columns=["brand", "model", "color", "specs"])
        st.download_button("📥 Download Model CSV Template", model_template.to_csv(index=False).encode(), "model-template.csv", "text/csv")
        # Upload CSV
        st.subheader("📂 Upload CSV to Add Models in Bulk")
        csv_model_file = st.file_uploader("Upload CSV with columns: model, color, specs", type="csv")
        # Process CSV
        if csv_model_file and "processed_bulk_upload_models" not in st.session_state:
            try:
                df = pd.read_csv(csv_model_file)
                df.columns = df.columns.str.lower()
                for _, row in df.iterrows():
                    cursor.execute("INSERT INTO models (brand, model, color, specs) VALUES (?, ?, ?, ?)",
                                (row["brand"], row["model"], row["color"], row["specs"]))
                conn.commit()
                st.success(f"{len(df)} models added successfully!")
                st.session_state.processed_bulk_upload_models = True
            except Exception as e:
                st.error(f"Error uploading models: {e}")
        # Delete model
        st.markdown("---")
        st.subheader("🗑️ Delete a Model Entry")

        # Smart select or input for Brand
        brands = df_models["brand"].unique().tolist()

        if "selected_brand" not in st.session_state:
            st.session_state.selected_brand = ""
        if "custom_brand" not in st.session_state:
            st.session_state.custom_brand = ""

        def on_select_brand():
            st.session_state.custom_brand = ""

        def on_custom_brand():
            st.session_state.selected_brand = ""

        st.selectbox("Select Existing Brand", options=[""] + brands, key="selected_brand", on_change=on_select_brand)
        

        # Use typed brand if provided, else selected
        brand = st.session_state.custom_brand.strip() if st.session_state.custom_brand.strip() else st.session_state.selected_brand

        if brand:
            filtered_by_brand = df_models[df_models["brand"] == brand]
            models = filtered_by_brand["model"].unique().tolist()

            if models:
                selected_model = st.selectbox("Select Model", models)
                filtered_by_model = filtered_by_brand[filtered_by_brand["model"] == selected_model]

                colors = filtered_by_model["color"].unique().tolist()
                selected_color = st.selectbox("Select Color", colors)

                filtered_by_color = filtered_by_model[filtered_by_model["color"] == selected_color]
                specs = filtered_by_color["specs"].unique().tolist()
                selected_specs = st.selectbox("Select Specifications", specs)

                if st.button("Delete Selected Model Entry"):
                    cursor.execute(
                        "DELETE FROM models WHERE brand = ? AND model = ? AND color = ? AND specs = ?",
                        (brand, selected_model, selected_color, selected_specs)
                    )
                    conn.commit()
                    st.success(f"Deleted model: {brand} / {selected_model} / {selected_color}")
                    st.rerun()
            else:
                st.info("No models found for selected brand.")
        else:
            st.warning("Please select or type a brand.")

            # Reset Table Option
            st.markdown("---")
            confirm_reset = st.checkbox("Are you sure you want to delete all models?")
            if st.button("Reset Models Table"):
                if confirm_reset:
                    cursor.execute("DELETE FROM models")
                    conn.commit()
                    st.success("All models have been deleted.")
                    st.rerun()
                else:
                    st.info("Please check the box to confirm before resetting the models.", icon="⚠️")

        # Distribuutor page - Display Existing Distributors
    elif st.session_state.page == "🏪 Add/Delete Distributor":
        st.title("📋 Existing Distributors")    
        df_dist = pd.read_sql_query("SELECT * FROM dist", conn)
        if df_dist.empty:
            st.info("No distributors available.")
        else:
            st.dataframe(df_dist, use_container_width=True)

            dist_ids = df_dist["id"].tolist()
            dist_id_to_delete = st.selectbox("Select Distributor ID to Delete", dist_ids)

            if st.button("Delete Selected Distributor"):
                cursor.execute("SELECT name FROM dist WHERE id = ?", (dist_id_to_delete,))
                dist_name = cursor.fetchone()[0]
                cursor.execute("DELETE FROM dist WHERE id = ?", (dist_id_to_delete,))
                cursor.execute("DELETE FROM users WHERE name = ? AND type = 'Guest'", (dist_name,))
                conn.commit()
                st.success("Distributor and corresponding Guest user deleted.")
                st.rerun()
        # Add Distributor form
        st.markdown("---")
        st.title("➕ Add Distributor")

        with st.form("add_distributor_form"):
            col1, col2 = st.columns(2)
            with col1:
                dist_name = st.text_input("Distributor Name").strip().upper()
                location = st.text_input("Location").strip().title()
                contact = st.text_input("Contact Number").strip()
            with col2:
                address = st.text_area("Address").strip().title()
                email = st.text_input("Email").strip()

            submit = st.form_submit_button("Add Distributor")

            if submit:
                if not dist_name or not address or not location or not contact or not email:
                    st.warning("Please fill in all fields.")
                else:
                    try:
                        cursor.execute("""
                            INSERT INTO dist (name, address, location, contact, email, added_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (dist_name, address, location, contact, email, st.session_state.username))
                        
                        cursor.execute("""
                            INSERT INTO users (name, type, pass) VALUES (?, 'Guest', '1234')
                        """, (dist_name,))
                        
                        conn.commit()
                        st.success(f"Distributor '{dist_name}' added with Guest login.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding distributor: {e}")
    else:
        st.title("🏠 Home")
        st.write("Welcome to the Model Manager dashboard.\n\nUse the sidebar to navigate through the application.")

# --- Close DB connection ---
conn.close()
