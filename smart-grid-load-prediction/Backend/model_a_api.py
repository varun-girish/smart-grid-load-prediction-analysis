import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)
CORS(app)

DATA_PATH = "/Users/varungirish/docs/college/3rd_sem/project/backend/model_a/MODEL_A_DATASET.csv"

# Load full dataset

df_full = pd.read_csv(DATA_PATH)

# API: Get list of states

@app.get("/states")
def get_states():
    states = sorted(df_full["State"].unique().tolist())
    return jsonify({"states": states})

# Helper: Train ARIMA + Predict N steps

def forecast_arima(series, steps):
    model = ARIMA(series, order=(2, 1, 2))
    model_fit = model.fit()
    preds = model_fit.forecast(steps=steps)
    return preds

# API: Predict future demand

@app.get("/predict")
def predict():
    state = request.args.get("state")
    n = int(request.args.get("n", 1))

    if state not in df_full["State"].unique():
        return jsonify({"error": "Invalid state"}), 400

    df_state = df_full[df_full["State"] == state].copy()
    df_state = df_state.sort_values("Year")

    historical_years = df_state["Year"].tolist()
    historical_values = df_state["Demand_MW"].tolist()

    last_actual_year = max(historical_years)  # Should be 2022

    # STEP 1: Predict 3 missing years (2023, 2024, 2025)

    extension_years_needed = 2025 - last_actual_year

    if extension_years_needed > 0:
        ext_preds = forecast_arima(historical_values, extension_years_needed)
        ext_years = list(range(last_actual_year + 1, 2026))

        for year, val in zip(ext_years, ext_preds):
            historical_years.append(year)
            historical_values.append(val)

    # historical covers 2015 → 2025

    # Predict user-requested forecast starting from 2026

    last_extended_year = max(historical_years)  # should be 2025
    future_start_year = last_extended_year + 1

    future_preds = forecast_arima(historical_values, n)
    future_years = list(range(future_start_year, future_start_year + n))

    predictions = [
        {"year": int(y), "demand_MW": float(v)}
        for y, v in zip(future_years, future_preds)
    ]

    return jsonify({
        "state": state,
        "historical_extended": [
            {"year": int(y), "demand_MW": float(v)}
            for y, v in zip(historical_years, historical_values)
        ],
        "predictions": predictions
    })

# Run server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)