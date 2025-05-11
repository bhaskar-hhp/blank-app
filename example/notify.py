import streamlit as st
import requests
 #it will work on root level only
# Ensure you have the required libraries installed
# pip install streamlit requests
# Streamlit app to send email notifications using Mailjet
# Set up Streamlit secrets
def send_mailjet_email(subject, message):
    api_key = st.secrets["mailjet"]["api_key"]
    api_secret = st.secrets["mailjet"]["api_secret"]
    from_email = st.secrets["mailjet"]["from_email"]
    to_email = st.secrets["mailjet"]["to_email"]

    url = "https://api.mailjet.com/v3.1/send"
    data = {
        "Messages": [
            {
                "From": {"Email": from_email, "Name": "Notifier"},
                "To": [{"Email": to_email, "Name": "User"}],
                "Subject": subject,
                "TextPart": message
            }
        ]
    }

    response = requests.post(url, auth=(api_key, api_secret), json=data)
    if response.status_code == 200:
        return "✅ Mailjet email sent successfully!"
    else:
        return f"❌ Mailjet email error: {response.text}"

# Streamlit UI
st.title("📧 Mailjet Email Notification Demo")

subject = st.text_input("Subject")
message = st.text_area("Message")

if st.button("Send Email"):
    if subject and message:
        status = send_mailjet_email(subject, message)
        if status.startswith("✅"):
            st.success(status)
        else:
            st.error(status)
    else:
        st.warning("Please enter both subject and message.")
