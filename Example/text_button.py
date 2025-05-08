import streamlit as st
import pandas as pd

name = st.text_input("Enter Your Name: ")
fname = st.text_input("Enter Fathers Name: ")
adr = st.text_area("Enter Your Address: ")
cls = st.selectbox("Enter Your Class: ",(1,2,3,4,5,6))

button = st.button("Done")
if button :
    st.markdown(f""" 
    Name : {name}
    Fathers Name : {fname}
    Address : {adr}
    Class : {cls}

    """)