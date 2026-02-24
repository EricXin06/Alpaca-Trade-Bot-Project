import pandas as pd
import matplotlib.pyplot as plt

def calculate_rsi(series, window=14):
    """
    Calculate the Relative Strength Index (RSI) for a given series.

    Parameters:
    - series: pandas Series, the data series for which RSI is calculated (e.g., closing prices).
    - window: int, the number of periods to use for the calculation (default is 14).

    Returns:
    - pandas Series with RSI values.
    """
    # Calculate price differences
    delta = series.diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Calculate RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def generate_signals(data, cooldown_period=5):
    """
    Generate buy and sell signals based on RSI with consecutive conditions and cooldown.

    Parameters:
    - data: DataFrame containing 'close' prices and 'RSI'.
    - cooldown_period: int, the number of periods to wait before generating a new signal.

    Returns:
    - Updated DataFrame with 'Signal' column.
    """
    data['Signal'] = 0  # Default to no signal
    last_trade_index = -cooldown_period  # Initialize with a negative cooldown

    for i in range(len(data)):
        if (data['RSI'].iloc[i] < 30 and data['RSI'].shift(1).iloc[i] < 30) and (i - last_trade_index >= cooldown_period):
            data['Signal'].iloc[i] = 1  # Buy signal
            last_trade_index = i
        elif (data['RSI'].iloc[i] > 70 and data['RSI'].shift(1).iloc[i] > 70) and (i - last_trade_index >= cooldown_period):
            data['Signal'].iloc[i] = -1  # Sell signal
            last_trade_index = i
    return data
