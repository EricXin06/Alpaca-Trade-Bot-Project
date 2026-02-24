from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import pandas as pd

# Alpaca credentials
ALPACA_API_KEY = "Insert Key"
ALPACA_SECRET_KEY = "Insert Secret Key"
BASE_URL = "https://paper-api.alpaca.markets/v2"


# Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

def map_timeframe(interval):
    """
    Map a string interval to Alpaca's TimeFrame object.

    Parameters:
    - interval: str, the desired interval ('minute', '15Min', '1H', '1D').

    Returns:
    - TimeFrame object.
    """
    if interval == 'minute':
        return TimeFrame.Minute
    elif interval == '15Min':
        return TimeFrame(15, TimeFrameUnit.Minute)
    elif interval == '1H':
        return TimeFrame.Hour
    elif interval == '1D':
        return TimeFrame.Day
    else:
        raise ValueError(f"Unsupported interval: {interval}")

def fetch_live_data(symbol, interval='minute', limit=1):
    """
    Fetch live stock data for the given symbol and interval.

    Parameters:
    - symbol: str, the stock symbol (e.g., 'AAPL').
    - interval: str, the data interval ('minute', '15Min', etc.).
    - limit: int, the number of bars to fetch (default: 1).

    Returns:
    - pandas DataFrame containing the live data.
    """
    try:
        # Map the interval to Alpaca's TimeFrame
        timeframe = map_timeframe(interval)

        # Fetch the latest bars
        bars = api.get_bars(symbol, timeframe, limit=limit)
        data = bars.df

        # Convert to New York timezone
        if not data.empty:
            data.index = data.index.tz_convert('America/New_York')

        print(f"Fetched live data for {symbol} ({interval}):")
        print(data.tail())  # Show the most recent bars for debug
        return data

    except Exception as e:
        print(f"Error fetching live data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_latest_trade(symbol):
    """
    Fetch the latest trade information for a symbol.

    Parameters:
    - symbol: str, the stock symbol.

    Returns:
    - dict containing the latest trade data.
    """
    try:
        trade = api.get_latest_trade(symbol)
        print(f"Latest trade for {symbol}: {trade}")
        return trade
    except Exception as e:
        print(f"Error fetching latest trade for {symbol}: {e}")
        return None
