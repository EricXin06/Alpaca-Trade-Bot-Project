import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def preprocess_data(data, window_size=60):
    """
    Prepares stock data for training an LSTM model.

    Parameters:
    - data: pandas DataFrame, stock price data (e.g., 'close' prices).
    - window_size: int, number of previous time steps to use for prediction.

    Returns:
    - X, y: Feature and target datasets for the model.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['close'].values.reshape(-1, 1))

    X, y = [], []
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i-window_size:i, 0])
        y.append(scaled_data[i, 0])

    return np.array(X), np.array(y), scaler

def build_lstm_model(input_shape):
    """
    Builds an LSTM model for stock price prediction.

    Parameters:
    - input_shape: tuple, shape of the input data (e.g., (60, 1)).

    Returns:
    - model: Compiled Keras LSTM model.
    """
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_predictive_model(data, window_size=60):
    """
    Trains an LSTM model on the provided stock data.

    Parameters:
    - data: pandas DataFrame, stock price data (e.g., 'close' prices).
    - window_size: int, number of previous time steps to use for prediction.

    Returns:
    - model: Trained LSTM model.
    - scaler: Scaler used to normalize the data.
    """
    X, y, scaler = preprocess_data(data, window_size)

    # Check for empty inputs
    if X.size == 0 or y.size == 0:
        raise ValueError("Insufficient data for training. Check the dataset and window size.")

    X = X.reshape(X.shape[0], X.shape[1], 1)  # Reshape for LSTM input

    # Split data into training and testing sets
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build and train the LSTM model
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, batch_size=32, epochs=20, validation_data=(X_test, y_test))

    return model, scaler
