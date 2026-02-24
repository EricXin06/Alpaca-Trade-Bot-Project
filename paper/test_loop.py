from utils.alpaca_fetcher_live import fetch_live_data
from indicators.rsi import calculate_rsi, generate_signals
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import time

# Alpaca API initialization
ALPACA_API_KEY = "Insert Key"
ALPACA_SECRET_KEY = "Insert Secret Key"
BASE_URL = "https://paper-api.alpaca.markets/v2"  # Switch to live API for live trading
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

def execute_trade(symbol, signal, qty=1):
    if signal == 1:
        print(f"Placing BUY order for {symbol}...")
        # Simulate order
    elif signal == -1:
        print(f"Placing SELL order for {symbol}...")
        # Simulate order
    else:
        print(f"No action taken for {symbol}. Signal: {signal}")

def fetch_historical_data(symbol, interval='1D', limit=100):
    try:
        if interval == 'minute':
            timeframe = TimeFrame.Minute
        elif interval == '15Min':
            timeframe = TimeFrame(15, TimeFrameUnit.Minute)
        elif interval == '1D':
            timeframe = TimeFrame.Day
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        print(f"Fetching historical data for {symbol} | Interval: {interval} | Limit: {limit}")
        bars = api.get_bars(symbol, timeframe, limit=limit)
        data = bars.df

        if not data.empty:
            data.index = data.index.tz_convert('America/New_York')
            print(f"Fetched {len(data)} rows for {symbol}")
        else:
            print("Fetched dataframe is empty.")

        return data
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return None

def simulate_trading(symbol, interval='1D', window=14, qty=1, cooldown_period=5):
    print(f"Starting simulated trading for {symbol}...")

    data = fetch_historical_data(symbol, interval=interval, limit=100)
    if data is None or data.empty:
        print(f"No historical data available for {symbol}.")
        return

    last_trade_time = None

    for i in range(window, len(data)):
        live_data = data.iloc[:i + 1]
        live_data['RSI'] = calculate_rsi(live_data['close'], window=window)
        live_data = generate_signals(live_data.copy(), cooldown_period=cooldown_period)

        latest_signal = live_data['Signal'].iloc[-1]
        print(f"Simulated RSI: {live_data['RSI'].iloc[-1]}, Signal: {latest_signal}")

        current_time = time.time()
        if last_trade_time is not None and current_time - last_trade_time < cooldown_period * 60:
            print("Cooldown period active. Skipping trade...")
            time.sleep(1)
            continue

        execute_trade(symbol, latest_signal, qty)
        last_trade_time = current_time

        time.sleep(1)

def main():
    symbol = 'AAPL'
    interval = '1D'
    qty = 10
    cooldown_period = 5

    simulate_trading(symbol, interval=interval, qty=qty, cooldown_period=cooldown_period)

if __name__ == "__main__":
    main()
