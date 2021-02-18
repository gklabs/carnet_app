import streamlit as st
import pandas as pd

st.title(" CAR-NET: Carbon Neutral Evaluation Tool")
st.write(" Created for Baltimore County by George Mason University")

Base_Budget = st.sidebar.number_input("Budget for 2021:")
st.write('Budget entered is', Base_Budget)
