import streamlit as st
import pandas as pd
import numpy as np

st.title(" CAR-NET: Carbon Neutral Evaluation Tool")
st.write(" Created for Baltimore County by George Mason University")

Base_Budget = st.sidebar.number_input("Enter Base Procurement Budget for 2021:")
st.write('Budget for 2021 entered is', Base_Budget)

df = pd.DataFrame(np.random.randn(50, 20),columns=('var %d' % i for i in range(20)))
st.dataframe(df)  # Same as st.write(df)

