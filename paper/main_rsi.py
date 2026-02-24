from utils.alpaca_fetcher import fetch_alpaca_data
from indicators.rsi import calculate_rsi, generate_signals
from backtest.backtesting import backtest_strategy
import matplotlib.pyplot as plt

def main():
    symbol = 'AAPL'
    interval = '1D'

    print("Fetching data from Alpaca...")
    data = fetch_alpaca_data(symbol, interval=interval, limit=100)
    if data is None or data.empty:
        print("No data fetched. Please check the symbol, interval, or Alpaca API settings.")
        return

    print("Fetched data:")
    print(data.head())
    print("Columns:", data.columns)

    print("Calculating RSI...")
    data['RSI'] = calculate_rsi(data['close'], window=14)
    data.dropna(subset=['RSI'], inplace=True)

    print("Generating signals...")
    data = generate_signals(data, cooldown_period=5)

    if data.empty or len(data) < 15:
        print("Not enough data after RSI calculation. Exiting.")
        return

    print(data[['close', 'RSI', 'Signal']].tail())

    print("Backtesting the strategy...")
    final_balance = backtest_strategy(data, initial_balance=100000, stop_loss=0.05, take_profit=0.10, position_size=0.1)

    print(f"Final Balance after backtesting: ${final_balance:.2f}")

    print("Visualizing results...")
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['close'], label='Close Price', color='blue')
    plt.plot(data.index, data['RSI'], label='RSI', color='orange')
    plt.axhline(y=70, color='red', linestyle='--', label='Overbought')
    plt.axhline(y=30, color='green', linestyle='--', label='Oversold')
    plt.title(f"{symbol} Price and RSI")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
