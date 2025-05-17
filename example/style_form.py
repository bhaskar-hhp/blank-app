import streamlit as st

st.set_page_config(page_title="Styled Form")

st.markdown("""
    <style>
    .custom-form {
        background-color: #497a78; /* Light blue */
        padding: 12px;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Use a container to hold the styled form
with st.container():
    st.markdown('<div class="custom-form">', unsafe_allow_html=True)

    with st.form("my_form"):
        st.subheader("📝 Styled Form")
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=1)
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success(f"Hello, {name}! You are {age} years old.")

    st.markdown('</div>', unsafe_allow_html=True)
