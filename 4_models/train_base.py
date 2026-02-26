import pandas as pd

print("✅ train_base.py is running...")

data = pd.read_csv("3_feature_engineering/final_ml_dataset.csv")

print("✅ Dataset loaded successfully!")
print("Shape:", data.shape)
print("Columns:", list(data.columns))


features = [
    "temp_c", "rainfall", "humidity", "lai",
    "pop_density", "urban_percent", "risk_index",
    "dengue_lag_1", "dengue_lag_2", "dengue_lag_3",
    "malaria_lag_1", "malaria_lag_2", "malaria_lag_3"
]

X = data[features]

def train_model(model, y, name):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    print("\n==============================")
    print(f"MODEL: {name}")
    print("RMSE:", round(rmse, 3))
    print("R2 Score:", round(r2, 3))
    print("==============================")

    return model, rmse, r2
