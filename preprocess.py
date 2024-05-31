import copy
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pickle
import lightgbm as lgb
from category_encoders import TargetEncoder, JamesSteinEncoder


def prepare():
    """Loads and prepares data from CSV files."""
    df = pd.read_csv('data.csv')
    return df


def process_price(df):
    price_std = df['price'].std()
    price_mean = df['price'].mean()
    lower_bound = price_mean - 3 * price_std
    upper_bound = price_mean + 3 * price_std
    df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]
    return df


def process_km(df):
    df = df[df['km'] >= 100]
    return df


def process_brand_and_model(df):
    target_enc = TargetEncoder()
    js_enc = JamesSteinEncoder()

    df['brand'] = target_enc.fit_transform(df['brand'], df['price'])
    df['model'] = js_enc.fit_transform(df['model'], df['price'])
    df['series'] = target_enc.fit_transform(df['series'], df['price'])

    return df


def process_engine_type(df):
    one_hot = OneHotEncoder()
    one_hot_engine_type = pd.get_dummies(df['engine_type'], prefix='engine_type')
    df = pd.concat([df, one_hot_engine_type], axis=1)
    return df


def process_transmission(df):
    df['transmission'] = df['transmission'].map({'Số tự động': 1, 'Số tay': 0})
    return df


def process_assemble_place(df):
    df['assemble_place'] = df['assemble_place'].map({'Nhập khẩu': 1, 'Lắp ráp trong nước': 0})
    return df


def preprocess(df):
    df = process_price(df)
    df = process_km(df)
    df = process_brand_and_model(df)
    df = process_engine_type(df)
    df = process_transmission(df)
    df = process_assemble_place(df)
    return df


def main():
    """Main function to run data preparation."""
    df = prepare()
    df = preprocess(df)
    df = df.drop(['engine_type', 'car_name', 'url'], axis=1)
    df.to_csv('data_preprocessed.csv', index=False)

if __name__ == '__main__':
    main()
