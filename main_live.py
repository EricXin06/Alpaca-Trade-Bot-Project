from utils.alpaca_fetcher_live import fetch_live_data
from indicators.rsi import calculate_rsi, generate_signals
from alpaca_trade_api.rest import REST
import time

import logging
from datetime import datetime

from key.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL

logging.basicConfig(
    filename='trading_log.txt',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_trade(symbol, action, qty, price):
    logging.info(f"{action.upper()} | {symbol} | Qty: {qty} | Price: ${price:.2f}")

# Alpaca API initialization
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

def execute_trade(symbol, signal, qty=1):
    """
    Execute a trade (buy/sell) based on the signal.

    Parameters:
    - symbol: str, the stock symbol to trade (e.g., 'AAPL').
    - signal: int, the trading signal (1 = buy, -1 = sell, 0 = no action).
    - qty: int, the number of shares to trade.
    """
    try:
        if signal == 1:  # Buy signal

            # Get account balance
            account = api.get_account()
            cash = float(account.cash)

                # Check if already holding the stock
            try:
                position = api.get_position(symbol)
                print(f"Already holding {position.qty} shares of {symbol}. Skipping buy.")
                return
            except:
                pass  # No position found, okay to continue

            # Check existing position and balance logic...
            price = api.get_latest_trade(symbol).price
            cost = price * qty
            if cash < cost:
                print(f"Not enough cash to buy {qty} shares of {symbol}. Needed: ${cost:.2f}")
                return

            print(f"Placing BUY order for {qty} shares of {symbol} at approx. ${price:.2f}")
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc"  # Good 'til canceled
            )
            print(f"BUY order placed successfully for {symbol}.")
            log_trade(symbol, "buy", qty, price)

        elif signal == -1:
            try:
                # Check if you own any shares of the symbol
                position = api.get_position(symbol)
                qty = int(position.qty)

                if qty > 0:
                    price = api.get_latest_trade(symbol).price
                    print(f"Placing SELL order for {qty} shares of {symbol} at approx. ${price:.2f}")
                    api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side="sell",
                        type="market",
                        time_in_force="gtc"
                    )
                    log_trade(symbol, "sell", qty, price)
                else:
                    print(f"No shares to sell for {symbol}. Position qty = 0.")
            except:
                print(f"No position to sell for {symbol}. Skipping sell order.")

        else:
            print(f"No trade executed for {symbol}. Signal: {signal}")

    except Exception as e:
        print(f"Error executing trade for {symbol}: {e}")

def is_market_open():
    """
    Check if the market is currently open.
    """
    try:
        clock = api.get_clock()
        if clock.is_open:
            print(f"Market is OPEN (Next Close: {clock.next_close}).")
            return True
        else:
            print(f"Market is CLOSED (Next Open: {clock.next_open}).")
            return False
    except Exception as e:
        print(f"Error checking market hours: {e}")
        return False

def process_live_data(symbol, interval='minute', window=14):
    """
    Fetch live data, calculate RSI, and generate signals.
    """
    data = fetch_live_data(symbol, interval=interval, limit=window + 1)
    if data is None or data.empty:
        print(f"No live data available for {symbol}.")
        return None

    # Calculate RSI and generate signals
    data['RSI'] = calculate_rsi(data['close'], window=window)
    data.dropna(subset=['RSI'], inplace=True)
    data = generate_signals(data.copy(), cooldown_period=5)

    print(f"Latest RSI and Signal for {symbol}:")
    print(data[['close', 'RSI', 'Signal']].tail())
    return data

def run_live_trading(symbol, interval='minute', qty=1, cooldown_period=5):
    """
    Run the live trading loop to fetch data, generate signals, and execute trades.

    Parameters:
    - symbol: str, the stock symbol to trade.
    - interval: str, the data interval ('minute', '15Min').
    - qty: int, the number of shares to trade per order.
    - cooldown_period: int, the cooldown period between trades (in minutes).
    """
    print(f"Starting live trading for {symbol}...")

    # Wait until the market is open
    while not is_market_open():
        print("Waiting for the market to open...")
        time.sleep(60)  # Check every 1 minute

    # Keep track of last trade to enforce cooldown
    last_trade_time = None

    while True:
        try:
            # Fetch and process live data
            data = process_live_data(symbol, interval=interval)
            if data is not None and not data.empty:
                # Get the latest signal
                latest_signal = data['Signal'].iloc[-1]
                print(f"Latest Signal for {symbol}: {latest_signal}")

                # Enforce cooldown period between trades
                current_time = time.time()
                if last_trade_time is not None and current_time - last_trade_time < cooldown_period * 60:
                    print("Cooldown period active. Skipping trade...")
                    time.sleep(60)
                    continue

                # Execute the trade based on the signal
                execute_trade(symbol, latest_signal, qty)
                last_trade_time = current_time

                account = api.get_account()
                print(f"Equity: ${account.equity}, Cash: ${account.cash}, Buying Power: ${account.buying_power}")
                
            else:
                print("No live data or signals available. Retrying in 1 minute...")

            # Wait for the next interval
            time.sleep(60)

        except KeyboardInterrupt:
            print("Live trading stopped by user.")
            break
        except Exception as e:
            print(f"Error in live trading loop: {e}")
            time.sleep(60)  # Retry after 1 minute

def main():
    symbol = 'AAPL'
    interval = 'minute'
    qty = 5      # Number of shares to trade
    cooldown_period = 5  # Cooldown period between trades (in minutes)

    run_live_trading(symbol, interval=interval, qty=qty, cooldown_period=cooldown_period)

if __name__ == "__main__":
    main()
