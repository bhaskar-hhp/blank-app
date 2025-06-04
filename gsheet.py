import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ledger Viewer", layout="centered")

st.title("📒 Ledger Viewer")

# Google Drive file IDs
file_id = '1Qt_dcHn8YNeVL6s7m7647YssIoukdNoB'
bal_file_id = '1F39ERDJAiRTOYnNTnThtF-sIl_-zX3j5'

# Construct direct download URLs
csv_url = f'https://drive.google.com/uc?id={file_id}'
bal_csv_url = f'https://drive.google.com/uc?id={bal_file_id}'

# Load CSVs
df = pd.read_csv(csv_url)
bal_df = pd.read_csv(bal_csv_url)

# UI block for ledger selection
st.subheader("🔍 Select Ledger")

if 'LedgerName' in df.columns:
    # Get unique ledger names
    ledger_options = df['LedgerName'].unique()

    # Selectbox for ledger selection
    selected_ledger = st.selectbox("Choose a Ledger", sorted(ledger_options))

    # Filter and display ledger data
    filtered_df = df[df['LedgerName'] == selected_ledger].drop(columns=['LedgerName'])
    st.subheader("📑 Ledger Details")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.error("❌ 'LedgerName' column not found in the main ledger data.")

# Show closing balance
if 'Ledger Name' in bal_df.columns:
    filtered_bal_df = bal_df[bal_df['Ledger Name'] == selected_ledger]
    if not filtered_bal_df.empty:
        closing_balance = filtered_bal_df['Closing Balance'].values[0]
        st.subheader("💰 Closing Balance")
        st.success(f"Closing Balance for **{selected_ledger}** is:   ₹ {closing_balance:,.2f}")
    else:
        st.warning("No balance information found for the selected ledger.")
else:
    st.error("❌ 'Ledger Name' column not found in the balance data.")
