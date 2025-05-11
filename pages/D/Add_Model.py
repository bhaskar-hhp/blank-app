import streamlit as st
import sqlite3
import pandas as pd

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

st.set_page_config(page_title="Add Model", page_icon="➕")
st.title("📋 Existing Models")

# --- Connect to DB ---
conn = sqlite3.connect("/workspaces/blank-app/data.db", check_same_thread=False)
cursor = conn.cursor()

# --- Ensure logged in ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

# --- Show existing models ---
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
        st.rerun()
    else:
        st.info("Please check the box to confirm before resetting the models.", icon="⚠️")

# --- Close connection ---
conn.close()
