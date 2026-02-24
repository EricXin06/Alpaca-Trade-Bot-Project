#paper
ALPACA_API_KEY = "Insert Key"
ALPACA_SECRET_KEY = "Insert Secret Key"
BASE_URL = "https://paper-api.alpaca.markets/v2"

#live
ALPACA_API_KEY = "Insert Key"
ALPACA_SECRET_KEY = "Insert Secret Key"
#BASE_URL = "https://api.alpaca.markets"

from alpaca_trade_api.rest import REST

# Set up Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url='https://paper-api.alpaca.markets')

# Get account details
account = api.get_account()
print(f"Account balance: ${account.cash}")


from alpaca_trade_api.rest import REST, TimeFrame

# Initialize API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url='https://paper-api.alpaca.markets')

# Fetch historical data
bars = api.get_bars("AAPL", TimeFrame.Day, limit=5)
data = bars.df
print(data)