import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

API_BASE = "http://localhost:5001"   # Model A API
WEATHER_API = "http://localhost:5003/latest_weather"  # Flask Weather API

st.title("SMART GRID - LOAD PREDICTION & ANALYSIS")

# ==========================================
# MODEL A SECTION
# ==========================================

st.header(" Model A - ARIMA Demand Forecasting")

@st.cache_data
def get_states():
    try:
        r = requests.get(f"{API_BASE}/states")
        return r.json().get("states", [])
    except:
        return []

states = get_states()

if not states:
    st.error("Model A API not running.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox("Select State", states)

with col2:
    n_years = st.slider("Years to Forecast", 1, 10, 5)

if st.button("Predict Demand (Model A)"):
    with st.spinner("Generating forecast..."):
        url = f"{API_BASE}/predict?state={state}&n={n_years}"
        out = requests.get(url).json()

        df_hist = pd.DataFrame(out["historical_extended"])
        df_hist["type"] = "Actual"

        df_pred = pd.DataFrame(out["predictions"])
        df_pred["type"] = "Forecast"

        df_hist = df_hist.rename(columns={"year": "Year", "demand_MW": "Demand_MW"})
        df_pred = df_pred.rename(columns={"year": "Year", "demand_MW": "Demand_MW"})

        combined = pd.concat([df_hist, df_pred])

    st.success("Forecast generated successfully!")

    fig = px.line(
        combined,
        x="Year",
        y="Demand_MW",
        color="type",
        markers=True,
        line_shape="spline",
        title=f"Demand Forecast for {state}"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast Table")
    st.dataframe(df_pred[["Year", "Demand_MW"]], use_container_width=True)

# ==========================================
# REAL TIME WEATHER SECTION (SEPARATE)
# ==========================================

st.markdown("---")
st.header(" Real-Time Weather Load Impact (Kafka + Flink)")

if st.button(" Start Real-Time Weather Monitoring"):

    st.info("Fetching live weather from Kafka stream...")

    placeholder = st.empty()

    for _ in range(20):   # fetch 20 updates
        try:
            res = requests.get(WEATHER_API).json()

            df_weather = pd.DataFrame([res])

            with placeholder.container():

                st.subheader(" Live Weather Data")

                st.dataframe(df_weather)

                # Temperature gauge style chart
                fig_temp = px.bar(
                    df_weather,
                    x="state",
                    y="temperature",
                    title="Live Temperature",
                    color="temperature"
                )

                st.plotly_chart(fig_temp, use_container_width=True)

                # Rainfall chart
                fig_rain = px.bar(
                    df_weather,
                    x="state",
                    y="rainfall",
                    title="Live Rainfall",
                    color="rainfall"
                )

                st.plotly_chart(fig_rain, use_container_width=True)

                st.subheader("⚡ Load Impact Classification")
                st.success(f"Load Impact: {res['load_impact']}")

        except:
            st.error("Weather API not reachable.")
            break

        time.sleep(2)