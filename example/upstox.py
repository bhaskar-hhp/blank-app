import streamlit as st
import pandas as pd
import requests

# === CONFIGURATION ===
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]

def fetch_holdings():
    url = "https://api.upstox.com/v2/portfolio/long-term-holdings"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        st.error(f"❌ Failed to fetch holdings: {e}")
        return []

# === STREAMLIT UI ===
st.set_page_config(page_title="Upstox Holdings", )
st.subheader("📊 Holdings Viewer")

holdings = fetch_holdings()

if holdings:
    df = pd.DataFrame(holdings)
    #st.dataframe(df)
    df["P&L ₹"] = df["pnl"].round(2)
    df["Avg Price ₹"] = df["average_price"].round(2)
    df["LTP ₹"] = df["last_price"].round(2)

    # Calculate P&L %
    df["Investment"] = df["quantity"] * df["Avg Price ₹"]
    df["P&L %"] = ((df["P&L ₹"] / df["Investment"]) * 100).round(2)

    
    df = df.rename(columns={
        "tradingsymbol": "Symbol",
        "quantity": "Qty"

    })
    display_df = df[["Symbol", "Qty", "Avg Price ₹", "LTP ₹", "P&L ₹", "P&L %"]]

    # Highlight profit/loss
    def highlight_pnl(val):
        return 'background-color: #d4edda; color: green;' if val > 0 else \
               'background-color: #f8d7da; color: red;'

    styled_df = display_df.style\
        .applymap(highlight_pnl, subset=["P&L ₹"])\
        .set_properties(**{
            'text-align': 'right'
        })

    # This ensures headers are centered too (optional)
    styled_df.set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'right')]}],
        overwrite=False
    )

    st.dataframe(
        display_df.style.applymap(highlight_pnl, subset=["P&L ₹"]),
        use_container_width=True
    )
else:
    st.info("No holdings found or unable to fetch data.")

    
