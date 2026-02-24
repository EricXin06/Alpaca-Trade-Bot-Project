from utils.alpaca_fetcher import fetch_alpaca_data
from indicators.rsi import calculate_rsi, generate_signals
from backtest.backtesting import backtest_strategy
from models.predictive_model import train_predictive_model
import matplotlib.pyplot as plt

def main():
    # Step 1: Fetch Data
    print("Fetching data from Alpaca...")
    data = fetch_alpaca_data('TSLA', interval='1D', limit=10000)

    # Check if data is empty
    if data is None or data.empty:
        print("No data fetched. Please check the symbol, interval, or Alpaca API settings.")
        return

    print("Fetched data:")
    print(data.head())
    print(f"Columns: {data.columns}")

    # Ensure 'close' column exists
    if 'close' not in data.columns:
        print("Error: 'close' column not found in the fetched data.")
        return

    # Check for minimum data length
    if len(data) <= 60:
        print("Not enough data to train the predictive model. Exiting...")
        return

    # Step 2: Train Predictive Model
    print("Training predictive model...")
    model, scaler = train_predictive_model(data, window_size=60)
    print("Predictive model trained successfully.")

    # Step 3: Add Predictions to the DataFrame
    print("Adding predictions...")
    predictions = []
    for i in range(60, len(data)):
        input_data = data['close'].values[i-60:i]
        scaled_data = scaler.transform(input_data.reshape(-1, 1)).reshape(1, 60, 1)
        predicted_price = scaler.inverse_transform(model.predict(scaled_data))[0][0]
        predictions.append(predicted_price)

    data['Predicted_Close'] = [None] * 60 + predictions
    print(data[['close', 'Predicted_Close']].tail())

    # Step 4: Calculate RSI and Generate Signals
    print("Calculating RSI...")
    data['RSI'] = calculate_rsi(data['close'], window=14)
    data.dropna(subset=['RSI'], inplace=True)

    print("Generating signals...")
    data = generate_signals(data.copy(), cooldown_period=5)  # Use .copy() to avoid SettingWithCopyWarning

    # Step 5: Backtest the Strategy
    print("Backtesting the strategy...")
    final_balance = backtest_strategy(data, initial_balance=100000, stop_loss=0.05, take_profit=0.10, position_size=0.1)
    print(f"Final Balance after backtesting: ${final_balance:.2f}")

    # Step 6: Visualize Results
    print("Visualizing results...")
    plot_results(data)

def plot_results(data):
    """
    Plot the closing prices, RSI, buy/sell signals, and predicted prices.
    """
    # Plot closing prices with buy/sell signals
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.title("Close Price with Buy/Sell Signals and Predicted Prices")
    plt.plot(data.index, data['close'], label='Close Price', color='blue')
    plt.plot(data.index, data['Predicted_Close'], label='Predicted Close', color='purple', linestyle='--')
    plt.scatter(data.index[data['Signal'] == 1], data['close'][data['Signal'] == 1], 
                label='Buy Signal', color='green', marker='^', alpha=1)
    plt.scatter(data.index[data['Signal'] == -1], data['close'][data['Signal'] == -1], 
                label='Sell Signal', color='red', marker='v', alpha=1)
    plt.legend()

    # Plot RSI with thresholds
    plt.subplot(2, 1, 2)
    plt.title("RSI with Buy/Sell Zones")
    plt.plot(data.index, data['RSI'], label='RSI', color='orange')
    plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
