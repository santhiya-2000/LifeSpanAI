import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler

WINDOW  = 30
RUL_CAP = 125

def get_column_names():
    return (
        ["unit_nr", "time_cycles"]
        + [f"op_setting_{i}" for i in range(1, 4)]
        + [f"sensor_{i}"     for i in range(1, 22)]
    )

def load_cmapss(subset="FD001",
                data_dir="dashboard/data/CMaps/"):
    if data_dir is None:
        base = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base, "data", "CMaps") + "/"
    cols = get_column_names()
    train = pd.read_csv(f"{data_dir}train_{subset}.txt",
                        sep=r"\s+", header=None).dropna(axis=1)
    test  = pd.read_csv(f"{data_dir}test_{subset}.txt",
                        sep=r"\s+", header=None).dropna(axis=1)
    rul   = pd.read_csv(f"{data_dir}RUL_{subset}.txt",
                        sep=r"\s+", header=None).dropna(axis=1)
    train.columns = cols
    test.columns  = cols
    rul.columns   = ["RUL"]

    # RUL labels
    max_cyc = train.groupby("unit_nr")["time_cycles"].max().reset_index()
    max_cyc.columns = ["unit_nr", "max_cycle"]
    train = train.merge(max_cyc, on="unit_nr")
    train["RUL"] = (train["max_cycle"] - train["time_cycles"]).clip(upper=RUL_CAP)
    train.drop(columns=["max_cycle"], inplace=True)

    # Feature selection by variance
    candidates = [c for c in train.columns
                  if c.startswith("op_setting_") or c.startswith("sensor_")]
    variances = train[candidates].var()
    sensor_cols = variances[variances > 1e-8].index.tolist()

    # Normalize
    scaler = MinMaxScaler()
    train[sensor_cols] = scaler.fit_transform(train[sensor_cols])
    test[sensor_cols]  = scaler.transform(test[sensor_cols])

    return train, test, rul, sensor_cols, scaler

def get_engine_window(df, engine_id, sensor_cols, window=WINDOW):
    """Return last WINDOW cycles for one engine as (1, window, features)."""
    eng  = df[df["unit_nr"] == engine_id].reset_index(drop=True)
    data = eng[sensor_cols].values
    if len(data) < window:
        pad  = np.zeros((window - len(data), data.shape[1]))
        data = np.vstack([pad, data])
    return data[-window:][np.newaxis, :, :].astype(np.float32)

def get_engine_full(df, engine_id, sensor_cols):
    """Return full history arrays for one engine."""
    eng = df[df["unit_nr"] == engine_id].reset_index(drop=True)
    return (eng[sensor_cols].values,
            eng["RUL"].values,
            eng["time_cycles"].values)

def get_rolling_predictions(model, df, engine_id,
                             sensor_cols, window=WINDOW):
    """Sliding window predictions across full engine history."""
    from model import predict_rul
    eng  = df[df["unit_nr"] == engine_id].reset_index(drop=True)
    data = eng[sensor_cols].values
    preds, cycles = [], []
    for i in range(len(data) - window + 1):
        w = data[i:i+window][np.newaxis, :, :].astype(np.float32)
        preds.append(predict_rul(model, w))
        cycles.append(eng["time_cycles"].iloc[i + window - 1])
    return np.array(preds), np.array(cycles)