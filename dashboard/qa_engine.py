import re

QA = {
    r'how many engine':     "The FD001 subset has 100 training engines and 100 test engines.",
    r'how many sensor':     "There are 21 raw sensors. After dropping low-variance ones, 14 remain.",
    r'what is rul':         "RUL (Remaining Useful Life) is the number of cycles an engine has left before failure.",
    r'what is rmse':        "RMSE (Root Mean Squared Error) measures prediction accuracy — lower is better.",
    r'what is mae':         "MAE (Mean Absolute Error) is the average prediction error in engine cycles.",
    r'what is shap':        "SHAP values show how much each sensor contributed to a specific RUL prediction.",
    r'what is (the )?window': "Each prediction uses the last 30 cycles of sensor readings as input.",
    r'what is (the )?cap':  "RUL is capped at 125 cycles — beyond that the engine is considered healthy.",
    r'which sensor':        "Top sensors by SHAP importance are typically s11, s4, s12, and s7.",
    r'how accurate':        "Our hybrid Transformer-LSTM achieves approximately RMSE ~12-14 on FD001.",
    r'what model':          "We use a Hybrid Transformer-LSTM: Transformer captures global attention, LSTM learns sequential degradation.",
    r'what dataset':        "We use the NASA CMAPSS Turbofan Engine Degradation Dataset (FD001-FD004).",
    r'how does (the )?model work': "The model takes 30 cycles of sensor data, passes it through a Transformer encoder for global attention, then an LSTM for sequential pattern learning, and outputs a single RUL value.",
    r'what is (the )?transformer': "The Transformer encoder uses self-attention to identify which time steps in the 30-cycle window are most critical for predicting degradation.",
    r'what is lstm':        "LSTM (Long Short-Term Memory) is a recurrent neural network that learns sequential patterns — used here to capture how degradation evolves over time.",
}

def answer(question: str) -> str:
    q = question.lower().strip()
    for pattern, response in QA.items():
        if re.search(pattern, q):
            return response
    return ("I don't have a specific answer for that. Try asking about: "
            "sensors, RUL, RMSE, MAE, SHAP, the model architecture, "
            "the dataset, or prediction accuracy.")