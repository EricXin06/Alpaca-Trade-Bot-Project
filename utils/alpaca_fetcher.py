from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

# Alpaca credentials
ALPACA_API_KEY = "Insert Key"
ALPACA_SECRET_KEY = "Insert Secret Key"
BASE_URL = "https://paper-api.alpaca.markets/v2"

# Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)


def map_timeframe(interval):
    if interval == 'minute':
        return TimeFrame.Minute
    elif interval == '15Min':
        return TimeFrame(15, TimeFrameUnit.Minute)  # Correctly create a 15-minute interval
    elif interval == '1H':  # 1-hour timeframe
        return TimeFrame.Hour
    elif interval == '1D':
        return TimeFrame.Day
    else:
        raise ValueError(f"Unsupported interval: {interval}")


def fetch_alpaca_data(symbol, interval='minute', limit=500):
    """
    Fetch historical data from Alpaca for a given symbol and interval.

    Parameters:
    - symbol: str, the stock symbol (e.g., 'AAPL', 'TSLA').
    - interval: str, the data interval ('minute', '15Min', '1D', etc.).
    - limit: int, the number of data points to fetch.

    Returns:
    - pandas DataFrame containing the historical data.
    """
    try:
        # Map the interval to TimeFrame
        timeframe = map_timeframe(interval)

        # Fetch bars
        bars = api.get_bars(symbol, timeframe, limit=limit)
        data = bars.df

        # Convert to market timezone
        if not data.empty:
            data.index = data.index.tz_convert('America/New_York')
        return data

    except Exception as e:
        print(f"Error fetching data for {symbol} with interval '{interval}': {e}")
        return None
