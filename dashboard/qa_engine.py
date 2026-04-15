import re

QA = {
    r'which engine.*risk|engine.*critical|most.*risk|at risk':
        "Based on current predictions, any engine with predicted RUL below 20 cycles is CRITICAL. "
        "In FD001, Engine 1 has only 2 cycles remaining - immediate maintenance required. "
        "Use the engine selector in the sidebar to check any specific engine's health status.",

    r'how many engine':
        "The FD001 subset has 100 training engines and 100 test engines.",

    r'how many sensor':
        "There are 21 raw sensors. After dropping low-variance ones, around 14 remain.",

    r'what is rul':
        "RUL (Remaining Useful Life) is the number of cycles an engine has left before failure.",

    r'what is rmse':
        "RMSE (Root Mean Squared Error) measures prediction accuracy; lower is better.",

    r'what is mae':
        "MAE (Mean Absolute Error) is the average prediction error in engine cycles.",

    r'what is shap':
        "SHAP values show how much each sensor contributed to a specific RUL prediction.",

    r'what is (the )?window':
        "Each prediction uses the last 30 cycles of sensor readings as input.",

    r'what is (the )?cap':
        "RUL is capped at 125 cycles beyond that the engine is considered healthy.",

    r'which sensor|top sensor|important sensor':
        "Top sensors by importance are sensor_12 (1.37), sensor_15 (1.35), and sensor_7 (1.06). "
        "These correspond to compressor efficiency and pressure ratio indicators.",

    r'how accurate|accuracy|performance':
        "LifeSpanAI achieves RMSE of 18.11 on FD002 and 18.37 on FD004 — "
        "best on complex multi-condition subsets where global attention helps most.",

    r'what model|which model|what architecture':
        "LifeSpanAI uses a Hybrid Transformer-LSTM: the Transformer encoder captures "
        "global attention across all 30 cycles, the LSTM learns sequential degradation patterns.",

    r'what dataset|what data':
        "We use the NASA CMAPSS Turbofan Engine Degradation Dataset (FD001–FD004), "
        "simulating jet engines running from healthy state to failure.",

    r'how does (the )?model work|how does it work':
        "The model takes 30 cycles of sensor data, passes it through a Transformer encoder "
        "for global attention, then two LSTM layers for sequential pattern learning, "
        "and outputs a single RUL value.",

    r'what is (the )?transformer':
        "The Transformer encoder uses self-attention to identify which of the 30 input cycles "
        "are most critical for predicting degradation cycle 26 gets highest attention.",

    r'what is lstm':
        "LSTM (Long Short-Term Memory) learns sequential patterns used here to capture "
        "how degradation evolves over time after the Transformer processes it.",

    r'what is fd001|what is fd002|what is fd003|what is fd004':
        "FD001: 1 condition, 1 fault, 100 engines (simplest). "
        "FD002: 6 conditions, 1 fault, 260 engines. "
        "FD003: 1 condition, 2 faults, 100 engines. "
        "FD004: 6 conditions, 2 faults, 248 engines (most complex).",

    r'how many subset|how many dataset':
        "There are 4 subsets: FD001, FD002, FD003, FD004 increasing in complexity.",

    r'critical|warning|healthy|status':
        "Engine status is determined by predicted RUL: "
        "CRITICAL = below 30 cycles, WARNING = 30–60 cycles, HEALTHY = above 60 cycles.",

    r'maintenance|when.*maintain|schedule':
        "LifeSpanAI recommends: schedule immediate shutdown if RUL < 10, "
        "plan maintenance within 5 cycles if RUL < 20, "
        "monitor closely if RUL < 60, continue normal operations if RUL > 60.",

    r'what is lifespanai|what is this':
        "LifeSpanAI is a predictive maintenance dashboard using a Hybrid Transformer-LSTM "
        "model to predict Remaining Useful Life of turbofan engines from sensor data.",
}

def answer(question: str) -> str:
    q = question.lower().strip()
    for pattern, response in QA.items():
        if re.search(pattern, q):
            return response
    return ("I don't have a specific answer for that. Try asking: "
            "'Which engine is at risk?', 'What is RUL?', "
            "'Which sensors matter most?', 'How accurate is the model?', "
            "or 'What is the model architecture?'")