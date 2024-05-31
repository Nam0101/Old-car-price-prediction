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
import category_encoders as ce

series_dict = {
    'SUV': 'SUV',
    'Sedan': 'Sedan',
    'Crossover': 'Crossover',
    'Hatchback': 'Hatchback',
    'Bán tải / Pickup': 'Pickup',
    'Van/Minivan': 'Van/Minivan',
    'Coupe': 'Coupe',
    'Convertible/Cabriolet': 'Convertible',
    'Truck': 'Truck',
    'MPV': 'MPV',
    'Bán Tải': 'Pickup',
    'Convertible': 'Convertible'
}


def prepare():
    """Loads and prepares data from CSV files."""
    df_bb = pd.read_csv('data_bonbanh.csv')
    df_oto = pd.read_csv('data_oto.csv')
    return df_bb, df_oto


def clean_duplicate(df):
    """Drops duplicate entries based on 'url' column."""
    df.drop_duplicates(subset=['url'], keep='first', inplace=True)
    return df


def process_price_bb(price):
    """Extracts numeric price from a string."""
    try:
        if 'Tỷ' in price:
            ty = float(price.split('Tỷ')[0])
            trieu = float(price.split('Tỷ')[1].split('Triệu')[0])
            return ty * 1000000000 + trieu * 1000000
        elif 'Triệu' in price:
            trieu = float(price.split('Triệu')[0].replace(' ', ''))
            return trieu * 1000000
        else:
            return 0
    except:
        return 0


def process_km_bb(df):
    """Cleans and converts 'km' column to numeric."""
    df.dropna(subset=['km'], inplace=True)
    df['km'] = df['km'].str.replace('Km', '').str.replace(',', '')
    df['km'] = pd.to_numeric(df['km'])
    df.drop(df[df['km'] < 1000].index, inplace=True)
    return df


def process_price_bb_apply(df):
    """Applies price processing to the 'price' column."""
    df['price'] = df['price'].apply(process_price_bb)
    df.drop(df[df['price'] == 0].index, inplace=True)
    return df


def process_brand_and_model(df):
    """Extracts 'brand' and 'model' from 'car_name'."""
    df['brand'] = df['car_name'].str.split().str[0]
    df['model'] = df['car_name'].str.split().str[1:].str.join(' ')
    return df


def other_process(df):
    """Groups infrequent brands into 'Other' category."""
    threshold = 10
    car_count = df['brand'].value_counts()
    small_brands = car_count[car_count < threshold].index.tolist()
    df['brand'] = df['brand'].apply(lambda x: 'Other' if x in small_brands else x)
    df['brand'].fillna('Other', inplace=True)
    return df


def process_engine_type(df):
    """Cleans and simplifies 'engine_type' column."""
    df['engine_type'] = df['engine_type'].apply(
        lambda x: df['engine_type'].value_counts().index[0] if x == '-' else x)
    df['engine_type'].fillna(df['engine_type'].value_counts().index[0], inplace=True)
    df['engine_type'] = df['engine_type'].str.split().str[0]
    return df


def process_transmission(df):
    """Cleans and simplifies 'transmission' column."""
    df['transmission'] = df['transmission'].apply(
        lambda x: df['transmission'].value_counts().index[0] if x == '-' else x)
    df['transmission'].fillna(df['transmission'].value_counts().index[0], inplace=True)
    return df


def process_year(df):
    """Applies year processing to the 'year' column."""
    df['year'] = pd.to_numeric(df['year'], errors='coerce')  # Convert to numeric directly
    df.dropna(subset=['year'], inplace=True)
    return df


def process_bonbanh(df_bb):
    """Applies all data processing steps to 'data_bonbanh.csv'."""
    df_bb = clean_duplicate(df_bb)
    df_bb = process_km_bb(df_bb)
    df_bb = process_price_bb_apply(df_bb)
    df_bb = process_brand_and_model(df_bb)
    df_bb = other_process(df_bb)
    df_bb = process_engine_type(df_bb)
    df_bb = process_transmission(df_bb)
    df_bb = process_year(df_bb)
    return df_bb


def process_price_oto(price):
    try:
        if price.find('tỉ') != -1:
            ty = price.split('tỉ')[0]
            trieu = price.split('tỉ')[1]
            trieu = trieu.split('triệu')[0]
            return float(ty) * 1000000000 + float(trieu) * 1000000
        elif price.find('triệu') != -1:
            trieu = price.split('triệu')[0]
            trieu = trieu.replace(' ', '')
            return float(trieu) * 1000000
        else:
            return 0
    except:
        return 0


def process_km_oto(df):
    df['km'] = df['km'].str.replace('km', '').str.replace('.', '')
    df['km'] = pd.to_numeric(df['km'])
    df.drop(df[df['km'] < 1000].index, inplace=True)
    return df


def process_price_oto_apply(df):
    df['price'] = df['price'].apply(process_price_oto)
    df.drop(df[df['price'] == 0].index, inplace=True)
    return df


def process_engine_type_oto(df):
    df['engine_type'] = df['engine_type'].str.split().str[1].str.capitalize()
    return df


def process_transmission_oto(df):
    df['transmission'] = df['transmission'].apply(lambda x: 'Số tay' if x == 'Số sàn' else 'Số tự động')
    return df


def process_assemble_place_oto(df):
    df['assemble_place'] = df['assemble_place'].apply(
        lambda x: 'Lắp ráp trong nước' if x == 'Trong nước' else 'Nhập khẩu')
    return df


def process_oto(df_oto):
    df_oto = clean_duplicate(df_oto)
    df_oto = process_km_oto(df_oto)
    df_oto = process_price_oto_apply(df_oto)
    df_oto = process_brand_and_model(df_oto)
    df_oto = other_process(df_oto)
    df_oto = process_engine_type_oto(df_oto)
    df_oto = process_transmission_oto(df_oto)
    df_oto = process_assemble_place_oto(df_oto)
    df_oto = process_year(df_oto)
    return df_oto


# thay these các giá trị null trong series bằng giá trị xuất hiện nhiều nhất
def fill_null(series):
    return series.fillna(series.value_counts().index[0])


def process_less_than_1_model(df):
    model_counts = df['model'].value_counts()

    # Danh sách các model chỉ xuất hiện một lần
    rare_models = model_counts[model_counts == 1].index

    # Thay thế các model hiếm bằng 'Other'
    df['model'] = df['model'].replace(rare_models, 'Other')
    return df


def main():
    """Main function to run data preparation."""
    df_bb, df_oto = prepare()
    df_bb = process_bonbanh(df_bb)
    df_oto = process_oto(df_oto)
    df = pd.concat([df_bb, df_oto], ignore_index=True)
    df['series'] = fill_null(df['series'])
    df['engine_type'] = fill_null(df['engine_type'])
    df['series'] = df['series'].map(series_dict)
    df = process_less_than_1_model(df)
    df.to_csv('data.csv', index=False)


if __name__ == '__main__':
    main()
