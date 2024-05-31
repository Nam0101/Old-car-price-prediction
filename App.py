from flask import Flask, request, jsonify
import pickle
import pandas as pd
from category_encoders import TargetEncoder, JamesSteinEncoder
from sklearn.preprocessing import OneHotEncoder
from flask_cors import CORS


# Initialize the Flask API
app = Flask(__name__)
CORS(app)

# Global variables for data and encoders
data = pd.read_csv('data/data.csv')
one_hot = OneHotEncoder()
target_enc = TargetEncoder()
js_enc = JamesSteinEncoder()
target_enc.fit(data['brand'], data['price'])
js_enc.fit(data['model'], data['price'])
target_enc_series = TargetEncoder()
target_enc_series.fit(data['series'], data['price'])
engine_type_enc = OneHotEncoder()
engine_type_enc.fit(data['engine_type'].values.reshape(-1, 1))
transmission_enc = OneHotEncoder()
transmission_enc.fit(data['transmission'].values.reshape(-1, 1))
assemble_place_enc = OneHotEncoder()
assemble_place_enc.fit(data['assemble_place'].values.reshape(-1, 1))
one_hot_engine_type = pd.get_dummies(data['engine_type'], prefix='engine_type')


def process(df):
    year = df['year'][0]
    brand = df['brand'][0]
    model = df['model'][0]
    series = df['series'][0]
    km = df['km'][0]
    engine_type = df['engine_type'][0]
    transmission = df['transmission'][0]  # Keep this as is
    assemble_place = df['assemble_place'][0]

    # Create a temporary DataFrame for transformation
    temp_df = pd.DataFrame({'brand': [brand], 'model': [model], 'series': [series]})

    temp_df['brand'] = target_enc.transform(temp_df[['brand']])
    temp_df['model'] = js_enc.transform(temp_df[['model']])
    temp_df['series'] = target_enc_series.transform(temp_df[['series']])

    # OneHotEncode 'engine_type' only
    engine_type = engine_type_enc.transform([[engine_type]])
    temp_df = pd.concat([temp_df, pd.DataFrame(engine_type.toarray(), columns=one_hot_engine_type.columns)], axis=1)

    # Add the 'transmission' and 'assemble_place' columns directly
    temp_df['transmission'] = [transmission]  # Add transmission as a separate column
    temp_df['assemble_place'] = [assemble_place]  # Add assemble_place as a separate column
    temp_df['transmission'] = temp_df['transmission'].map({'Số tự động': 1, 'Số tay': 0})
    temp_df['assemble_place'] = temp_df['assemble_place'].map({'Nhập khẩu': 1, 'Lắp ráp trong nước': 0})
    temp_df['year'] = year
    temp_df['km'] = km
    return temp_df


def convert_to_vnd(price):
    if price >= 1_000_000_000:
        billions = price // 1_000_000_000
        millions = (price % 1_000_000_000) // 1_000_000
        return f"{billions} tỷ {millions} triệu"
    elif price >= 1_000_000:
        return f"{price // 1_000_000} triệu"
    else:
        return f"{price} đồng"


# Create the API route
@app.route('/predict', methods=['POST'])
def predict():
    model = pickle.load(open('finalized_model.pkl', 'rb'))
    req = request.get_json()
    df = pd.DataFrame([req])
    df = process(df)
    df = df[['year', 'assemble_place', 'series', 'km', 'transmission', 'brand', 'model', 'engine_type_Dầu',
             'engine_type_Hybrid', 'engine_type_Xăng', 'engine_type_Điện']]
    prediction = model.predict(df)[0]
    print(prediction.tolist())
    low_price = prediction * 0.9
    high_price = prediction * 1.1
    prediction = convert_to_vnd(prediction)
    low_price = convert_to_vnd(low_price)
    high_price = convert_to_vnd(high_price)

    return jsonify({'price': prediction, 'low_price': low_price, 'high_price': high_price})


@app.route('/brands', methods=['GET'])
def brands():
    return jsonify(data['brand'].dropna().unique().tolist())


@app.route('/models', methods=['GET'])
def models():
    return jsonify(data['model'].dropna().unique().tolist())


@app.route('/series', methods=['GET'])
def series():
    return jsonify(data['series'].dropna().unique().tolist())


@app.route('/engine_types', methods=['GET'])
def engine_types():
    return jsonify(data['engine_type'].dropna().unique().tolist())


@app.route('/transmissions', methods=['GET'])
def transmissions():
    return jsonify(data['transmission'].dropna().unique().tolist())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
