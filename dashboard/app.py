import os
import math
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gauge import get_gauge_html

from data_loader import (load_cmapss, get_engine_window,
                         get_engine_full, get_rolling_predictions)
from model import load_model, predict_rul
from qa_engine import answer

st.set_page_config(
    page_title="LifeSpanAI Dashboard",
    page_icon="⚙️",
    layout="wide"
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ── Gauge function ────────────────────────────────
def draw_gauge(rul_value, max_rul=125):
    pct   = min(rul_value / max_rul, 1.0)
    angle = 180 + pct * 180
    rad   = math.radians(angle)
    cx, cy, r = 130, 120, 90
    nx = cx + r * math.cos(rad)
    ny = cy + r * math.sin(rad)

    if rul_value <= 20:
        needle_color = "#DC2626"
    elif rul_value <= 60:
        needle_color = "#F59E0B"
    else:
        needle_color = "#10B981"

    return f"""
    <svg width="260" height="140" viewBox="0 0 260 140"
         xmlns="http://www.w3.org/2000/svg">
      <path d="M 40 120 A 90 90 0 0 1 220 120"
            fill="none" stroke="#e5e7eb" stroke-width="18" stroke-linecap="round"/>
      <path d="M 40 120 A 90 90 0 0 1 72 49"
            fill="none" stroke="#DC2626" stroke-width="18"
            stroke-linecap="butt" opacity="0.85"/>
      <path d="M 72 49 A 90 90 0 0 1 155 31"
            fill="none" stroke="#F59E0B" stroke-width="18"
            stroke-linecap="butt" opacity="0.85"/>
      <path d="M 155 31 A 90 90 0 0 1 220 120"
            fill="none" stroke="#10B981" stroke-width="18"
            stroke-linecap="butt" opacity="0.85"/>
      <line x1="{cx}" y1="{cy}"
            x2="{nx:.1f}" y2="{ny:.1f}"
            stroke="{needle_color}" stroke-width="3" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="6" fill="{needle_color}"/>
      <text x="{cx}" y="{cy - 22}"
            text-anchor="middle" font-size="28"
            font-weight="bold" fill="{needle_color}">{int(rul_value)}</text>
      <text x="{cx}" y="{cy - 6}"
            text-anchor="middle" font-size="11"
            fill="#6b7280">cycles remaining</text>
      <text x="28"  y="136" font-size="10" fill="#DC2626">0</text>
      <text x="222" y="136" font-size="10" fill="#10B981">125</text>
    </svg>
    """

# ── Find model file ───────────────────────────────
def find_model(subset, assets_dir):
    import glob
    patterns = [
        f"best_model_{subset}_Hybrid_Transformer_LSTM.h5",
        f"best_model_{subset}_Transformer_Only.h5",
        f"best_model_{subset}_Transformer-only.h5",
    ]
    for p in patterns:
        path = os.path.join(assets_dir, p)
        if os.path.exists(path):
            return path
    matches = glob.glob(os.path.join(assets_dir, f"best_model_{subset}_*.h5"))
    return matches[0] if matches else None

# ── Cache data & model ────────────────────────────
@st.cache_resource
def setup(subset):
    train, test, rul, sensor_cols, scaler = load_cmapss(subset)
    model_path = find_model(subset, ASSETS_DIR)
    model = load_model(model_path) if model_path else None
    return train, test, rul, sensor_cols, scaler, model

# ── Sidebar ───────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(BASE_DIR, "assets", "LifeSpanAI_Logo.jpeg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.title("LifeSpanAI")

    st.caption("Hybrid Transformer-LSTM · NASA CMAPSS")
    st.divider()

    subset     = st.selectbox("Dataset subset",
                               ["FD001","FD002","FD003","FD004"])
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

# ── Header ────────────────────────────────────────
st.title("LifeSpanAI - Predictive Maintenance Dashboard")
st.caption(f"NASA CMAPSS {subset}  ·  Hybrid Transformer-LSTM model")
st.divider()

if model is None:
    st.error("Model file not found in dashboard/assets/ — "
             "place your .h5 file there.")
    st.stop()

# ── Engine data & prediction ──────────────────────
data, true_rul, cycles = get_engine_full(train, engine_id, sensor_cols)
window_arr = get_engine_window(train, engine_id, sensor_cols)
pred_rul   = predict_rul(model, window_arr)
true_final = float(true_rul[-1])
error      = abs(pred_rul - true_final)
status     = "CRITICAL" if pred_rul < 30 else "WARNING" if pred_rul < 60 else "HEALTHY"
status_col = "red"      if pred_rul < 30 else "orange"  if pred_rul < 60 else "green"

# ── KPI row ───────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Predicted RUL", f"{pred_rul:.0f} cycles")
c2.metric("True RUL",      f"{true_final:.0f} cycles")
c3.metric("Error",         f"{error:.1f} cycles")
c4.metric("Total cycles",  f"{len(cycles)}")
c5.markdown(f"**Engine status**  \n:{status_col}[{status}]")

st.divider()
# ── Risk Gauge + Recommendation ───────────────────
col_gauge, col_rec = st.columns([1, 2])

with col_gauge:
    st.subheader("Engine health gauge")
    gauge_html = get_gauge_html(pred_rul)
    components.html(gauge_html, height=320)

with col_rec:
    st.subheader("Maintenance recommendation")

    if pred_rul <= 10:
        st.error(
            f"IMMEDIATE ACTION REQUIRED — Engine failure imminent within "
            f"{int(pred_rul)} cycles. Schedule emergency shutdown now."
        )
    elif pred_rul <= 20:
        st.error(
            f"CRITICAL — Schedule maintenance within the next 5 cycles. "
            f"Only {int(pred_rul)} cycles remaining."
        )
    elif pred_rul <= 60:
        st.warning(
            f"WARNING — Plan maintenance in the next scheduled window. "
            f"{int(pred_rul)} cycles remaining. "
            f"Monitor sensor_12 and sensor_15 closely."
        )
    else:
        st.success(
            f"HEALTHY — Engine operating normally with {int(pred_rul)} "
            f"cycles remaining. Next check-in when RUL drops below 60."
        )

    st.markdown("**Top degradation signals**")
    top_sensors    = ["sensor_12", "sensor_15", "sensor_7"]
    top_importance = [1.37, 1.35, 1.06]
    for s_name, imp in zip(top_sensors, top_importance):
        pct = int((imp / 1.4) * 100)
        st.markdown(
            f"`{s_name}` &nbsp;"
            f'<div style="display:inline-block; width:{pct}%; height:8px;'
            f'background:#1E2761; border-radius:4px; vertical-align:middle;">'
            f'</div> &nbsp; {imp:.2f}',
            unsafe_allow_html=True
        )

st.divider()

# ── Charts row ────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader(f"Sensor {sensor} — degradation trend")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(cycles, data[:, sensor_cols.index(sensor)],
            color="steelblue", linewidth=1.5)
    ax.set_xlabel("Cycle")
    ax.set_ylabel(f"{sensor} (normalized)")
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig)
    plt.close()

with col_r:
    st.subheader("Predicted vs true RUL over time")
    with st.spinner("Computing rolling predictions..."):
        preds_roll, pred_cycles = get_rolling_predictions(
            model, train, engine_id, sensor_cols)
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.plot(cycles,      true_rul,   color="green",
             linewidth=1.5, label="True RUL")
    ax2.plot(pred_cycles, preds_roll, color="tomato",
             linewidth=1.5, linestyle="--", label="Predicted RUL")
    ax2.set_xlabel("Cycle")
    ax2.set_ylabel("RUL (cycles)")
    ax2.legend()
    ax2.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig2)
    plt.close()

st.divider()

# ── Feature importance ────────────────────────────
st.subheader("Feature importance — permutation method")
with st.spinner("Computing feature importance..."):
    try:
        from sklearn.metrics import mean_squared_error as mse
        X_test_all = np.array([
            get_engine_window(test, eid, sensor_cols)[0]
            for eid in sorted(test["unit_nr"].unique())
        ])
        y_test_all = rul_df["RUL"].values.clip(max=125).astype(np.float32)
        baseline   = np.sqrt(mse(y_test_all,
                        model.predict(X_test_all, verbose=0).flatten()))
        importances = []
        for j in range(X_test_all.shape[2]):
            X_p = X_test_all.copy()
            np.random.shuffle(X_p[:, :, j])
            importances.append(
                np.sqrt(mse(y_test_all,
                    model.predict(X_p, verbose=0).flatten())) - baseline)
        imp_df = pd.DataFrame({
            "Feature": sensor_cols,
            "Importance": importances
        }).sort_values("Importance", ascending=True).tail(15)
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.barh(imp_df["Feature"], imp_df["Importance"], color="steelblue")
        ax3.set_xlabel("Increase in RMSE when feature is shuffled")
        ax3.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig3)
        plt.close()
    except Exception as e:
        st.info(f"Feature importance unavailable: {e}")

st.divider()

# ── Q&A ───────────────────────────────────────────
st.subheader("Ask a question about the model or dataset")
if "history" not in st.session_state:
    st.session_state.history = []

question = st.chat_input(
    "e.g. What is RUL? Which sensors matter most?")
if question:
    st.session_state.history.append(("user", question))
    st.session_state.history.append(("bot", answer(question)))

for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)