import streamlit as st
import pandas as pd
import pickle as pkl
import numpy as np
st.markdown("<h1 style='text-align: center; color: red;'>Car Price Predictor</h1>",
            unsafe_allow_html=True)
st.sidebar.write("# Car Information")
st.sidebar.write("## Select the car features")
data = pd.read_csv("data/data.csv")
data = data.drop(["Unnamed: 0"], axis=1)
model = pkl.load(open('notebooks/RandomeForestModel.pkl.pkl', 'rb'))


def predict(a, b, c, d, e, f, g, h, i):
    price = model.predict(pd.DataFrame(columns=['engine_type', 'series', 'model', 'brand', 'year', 'driven kms',
                          'num_of_seat', 'transmission', 'assemble_place'], data=np.array([a, b, c, d, e, f, g, h, i]).reshape(1, 9)))
    return st.write("The Reselling Price of", e, a, "borrowed in the year", c, "is", float(price))
