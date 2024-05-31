import copy
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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
from sklearn.model_selection import KFold, RandomizedSearchCV


def prepare():
    """Loads and prepares data from CSV files."""
    df = pd.read_csv('data_preprocessed.csv')
    return df


def splitXandY(df):
    X = df.drop('price', axis=1)
    y = df['price']
    return X, y


def split_train_test(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test


def train_model_LinearRegression(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def train_model_LGBM(X_train, y_train):
    model = lgb.LGBMRegressor()
    model.fit(X_train, y_train)
    return model


def train_model_RandomForest(X_train, y_train):
    rf = RandomForestRegressor(n_estimators=100)
    rf.get_params()
    rf_hyperparams = {
        'n_estimators': [200, 300, 400, 500],
        'max_depth': [None, 10, 50, 90, 110],
        'max_features': ['sqrt'],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }

    rf_randomized_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=rf_hyperparams,
        n_iter=10,
        cv=KFold(n_splits=10, shuffle=True, random_state=42),
        verbose=2,
        random_state=42,
        n_jobs=-1
    )
    rf_randomized_search.fit(X_train, y_train)
    return rf_randomized_search


def train_model_GradientBoostingRegressor(X_train, y_train):
    model = GradientBoostingRegressor()
    model.fit(X_train, y_train)
    return model


def train_model():
    df = prepare()
    X, y = splitXandY(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    # Train all models
    model_LinearRegression = train_model_LinearRegression(X_train, y_train)
    model_LGBM = train_model_LGBM(X_train, y_train)
    model_RandomForest = train_model_RandomForest(X_train, y_train)
    model_GradientBoostingRegressor = train_model_GradientBoostingRegressor(X_train, y_train)

    # Evaluate models on test set
    scores = {
        "LinearRegression": model_LinearRegression.score(X_test, y_test),
        "LGBM": model_LGBM.score(X_test, y_test),
        "RandomForest": model_RandomForest.score(X_test, y_test),
        "GradientBoostingRegressor": model_GradientBoostingRegressor.score(X_test, y_test)
    }
    print(scores)
    # lấy ra model có score cao nhất
    best_model_name = max(scores, key=scores.get)
    print("Best model: ", best_model_name)
    if best_model_name == "LinearRegression":
        return model_LinearRegression
    elif best_model_name == "LGBM":
        return model_LGBM
    elif best_model_name == "RandomForest":
        return model_RandomForest
    else:
        return model_GradientBoostingRegressor


def main():
    model = train_model()
    with open('model.pkl', 'wb') as model_file:
        pickle.dump(model, model_file)



