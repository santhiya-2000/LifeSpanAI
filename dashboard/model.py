import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Dense, LSTM, Dropout, Conv1D, MaxPooling1D,
    GlobalAveragePooling1D, LayerNormalization, MultiHeadAttention, Add
)
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam

LR = 1e-3

def transformer_encoder_block(x, head_size=8, num_heads=2,
                               ff_dim=16, dropout=0.2):
    attn = MultiHeadAttention(
        num_heads=num_heads, key_dim=head_size, dropout=dropout)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization(epsilon=1e-6)(x)
    ff = Dense(ff_dim, activation="relu")(x)
    ff = Dropout(dropout)(ff)
    ff = Dense(x.shape[-1])(ff)
    x = Add()([x, ff])
    x = LayerNormalization(epsilon=1e-6)(x)
    return x

def build_hybrid_transformer_lstm(input_shape):
    inp = Input(shape=input_shape)
    x = transformer_encoder_block(inp)
    x = LSTM(16, return_sequences=True)(x)
    x = Dropout(0.2)(x)
    x = LSTM(8)(x)
    x = Dropout(0.2)(x)
    out = Dense(1)(x)
    model = Model(inp, out, name="Hybrid_Transformer_LSTM")
    model.compile(optimizer=Adam(LR), loss="mean_squared_error", metrics=["mae"])
    return model

class CompatDense(tf.keras.layers.Dense):
    @classmethod
    def from_config(cls, config):
        config.pop("quantization_config", None)
        return super().from_config(config)

def load_model(path):
    """Load a saved .h5 Keras model safely across minor version differences."""
    return tf.keras.models.load_model(
        path,
        custom_objects={"Dense": CompatDense},
        compile=False
    )

def predict_rul(model, window_array):
    pred = model.predict(window_array, verbose=0)
    return float(pred.flatten()[0])