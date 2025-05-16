import streamlit as st
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

# --- Email Notification Function ---
def send_email(subject, message, to_email):
    from_email = st.secrets["email"]["from_email"]
    password = st.secrets["email"]["app_password"]

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        return "✅ Email sent!"
    except Exception as e:
        return f"❌ Email error: {e}"

# --- WhatsApp Notification Function ---
def send_whatsapp(to_number, message):
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]
    from_number = 'whatsapp:+14155238886'  # Twilio sandbox number

    client = Client(account_sid, auth_token)
    try:
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to='whatsapp:' + to_number
        )
        return f"✅ WhatsApp sent: SID {msg.sid}"
    except Exception as e:
        return f"❌ WhatsApp error: {e}"

# --- Streamlit UI ---
st.title("🔔 Notification Sender")

st.header("📧 Send Email")
email = st.text_input("Recipient Email")
subject = st.text_input("Subject")
email_msg = st.text_area("Email Message")
if st.button("Send Email"):
    if email and subject and email_msg:
        result = send_email(subject, email_msg, email)
        st.success(result)
    else:
        st.warning("Please fill all email fields.")

st.header("💬 Send WhatsApp")
whatsapp_number = st.text_input("WhatsApp Number (with country code, e.g., +91...)")
whatsapp_msg = st.text_area("WhatsApp Message")
if st.button("Send WhatsApp"):
    if whatsapp_number and whatsapp_msg:
        result = send_whatsapp(whatsapp_number, whatsapp_msg)
        st.success(result)
    else:
        st.warning("Please fill all WhatsApp fields.")
