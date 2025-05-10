import streamlit as st
import pandas as pd

dataset = pd.read_csv("test.csv")

st.dataframe(dataset)
