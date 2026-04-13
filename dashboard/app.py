import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from data_loader import (load_cmapss, get_engine_window,
                         get_engine_full, get_rolling_predictions)
from model import load_model, predict_rul
from qa_engine import answer
import glob

def find_model(subset, assets_dir):
    patterns = [
        f"best_model_{subset}_Transformer_Only.h5",
        f"best_model_{subset}_Transformer-only.h5",
        f"best_model_{subset}_Hybrid_Transformer_LSTM.h5",
    ]
    for p in patterns:
        path = os.path.join(assets_dir, p)
        if os.path.exists(path):
            return path
    matches = glob.glob(os.path.join(assets_dir, f"best_model_{subset}_*.h5"))
    return matches[0] if matches else None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "CMaps") + "/"
ASSETS_DIR = os.path.join(BASE_DIR, "assets") + "/"

st.set_page_config(
    page_title="LifeSpanAI Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# ── Cache data & model ───────────────────────────
@st.cache_resource
def setup(subset):
    train, test, rul, sensor_cols, scaler = load_cmapss(subset)
    model_path = find_model(subset, ASSETS_DIR)
    model = load_model(model_path) if model_path else None
    return train, test, rul, sensor_cols, scaler, model


# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.image("dashboard/LifeSpanAI_Logo.jpeg", width=200)
    st.title("LifeSpanAI — Predictive Maintenance")
    st.caption("Hybrid Transformer-LSTM")
    st.divider()

    subset    = st.selectbox("Dataset subset", ["FD001","FD002","FD003","FD004"])
    train, test, rul_df, sensor_cols, scaler, model = setup(subset)

    engine_ids = sorted(train["unit_nr"].unique())
    engine_id  = st.selectbox("Select engine", engine_ids)
    sensor     = st.selectbox("Sensor to plot", sensor_cols)
    st.divider()
    st.markdown(f"**Subset:** {subset}  \n"
                f"**Engines:** {len(engine_ids)}  \n"
                f"**Features:** {len(sensor_cols)}  \n"
                f"**Window:** 30 cycles  \n"
                f"**RUL cap:** 125 cycles")

# ── Main header ──────────────────────────────────
st.title("LifeSpanAI — Predictive Maintenance Dashboard")
st.caption(f"NASA CMAPSS {subset}  ·  Hybrid Transformer-LSTM model")
st.divider()

# ── Get engine data ──────────────────────────────
data, true_rul, cycles = get_engine_full(train, engine_id, sensor_cols)
window_arr = get_engine_window(train, engine_id, sensor_cols)

if model is not None:
    pred_rul   = predict_rul(model, window_arr)
    true_final = float(true_rul[-1])
    error      = abs(pred_rul - true_final)
    status     = "CRITICAL" if pred_rul < 30 else "WARNING" if pred_rul < 60 else "HEALTHY"
    status_col = "red"      if pred_rul < 30 else "orange"  if pred_rul < 60 else "green"
else:
    st.warning("Model file not found in dashboard/assets/ — place your .h5 file there.")
    st.stop()

# ── KPI row ──────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Predicted RUL",  f"{pred_rul:.0f} cycles")
c2.metric("True RUL",       f"{true_final:.0f} cycles")
c3.metric("Error",          f"{error:.1f} cycles")
c4.metric("Total cycles",   f"{len(cycles)}")
c5.markdown(f"**Engine status**  \n :{status_col}[{status}]")

st.divider()

# ── Charts row ───────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader(f"Sensor {sensor} — degradation trend")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(cycles, data[:, sensor_cols.index(sensor)],
            color="steelblue", linewidth=1.5)
    ax.set_xlabel("Cycle")
    ax.set_ylabel(f"{sensor} (normalized)")
    ax.spines[["top","right"]].set_visible(False)
    st.pyplot(fig)
    plt.close()

with col_r:
    st.subheader("Predicted vs true RUL over time")
    preds_roll, pred_cycles = get_rolling_predictions(
        model, train, engine_id, sensor_cols)
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.plot(cycles,      true_rul,    color="green",
             linewidth=1.5, label="True RUL")
    ax2.plot(pred_cycles, preds_roll,  color="tomato",
             linewidth=1.5, linestyle="--", label="Predicted RUL")
    ax2.set_xlabel("Cycle")
    ax2.set_ylabel("RUL (cycles)")
    ax2.legend()
    ax2.spines[["top","right"]].set_visible(False)
    st.pyplot(fig2)
    plt.close()

st.divider()

# ── Feature importance ───────────────────────────
st.subheader("Feature importance — permutation method")
try:
    from sklearn.metrics import mean_squared_error as mse

    X_test_all = np.array([
        get_engine_window(test, eid, sensor_cols)[0]
        for eid in sorted(test["unit_nr"].unique())
    ])
    y_test_all = rul_df["RUL"].values.clip(max=125).astype(np.float32)

    baseline_rmse = np.sqrt(mse(y_test_all,
        model.predict(X_test_all, verbose=0).flatten()))

    importances = []
    for j in range(X_test_all.shape[2]):
        X_perm = X_test_all.copy()
        np.random.shuffle(X_perm[:, :, j])
        rmse_j = np.sqrt(mse(y_test_all,
            model.predict(X_perm, verbose=0).flatten()))
        importances.append(rmse_j - baseline_rmse)

    imp_df = pd.DataFrame({
        "Feature":    sensor_cols,
        "Importance": importances
    }).sort_values("Importance", ascending=True).tail(15)

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.barh(imp_df["Feature"], imp_df["Importance"], color="steelblue")
    ax3.set_xlabel("Increase in RMSE when shuffled")
    ax3.spines[["top","right"]].set_visible(False)
    st.pyplot(fig3)
    plt.close()

except Exception as e:
    st.info(f"Feature importance unavailable: {e}")

st.divider()

# ── Q&A ──────────────────────────────────────────
st.subheader("Ask a question about the model or dataset")
if "history" not in st.session_state:
    st.session_state.history = []

question = st.chat_input("e.g. What is RUL? Which sensors matter most?")
if question:
    st.session_state.history.append(("user", question))
    st.session_state.history.append(("bot",  answer(question)))

for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)