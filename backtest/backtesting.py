def backtest_strategy(data, initial_balance=100000, stop_loss=0.05, take_profit=0.10, position_size=0.1):
    """
    Backtest the RSI trading strategy with stop-loss, take-profit, and position sizing.

    Parameters:
    - data: DataFrame containing 'close' prices and 'Signal'.
    - initial_balance: Initial account balance.
    - stop_loss: Stop-loss threshold as a percentage (default is 5%).
    - take_profit: Take-profit threshold as a percentage (default is 10%).
    - position_size: Fraction of balance to use for each trade (default is 10%).

    Returns:
    - final_balance: Balance after executing the strategy.
    """
    balance = initial_balance
    position = 0  # Tracks the number of shares held
    buy_price = 0  # Tracks the purchase price of the position

    for i in range(len(data)):
        # Buy signal
        if data['Signal'].iloc[i] == 1 and position == 0:
            trade_value = balance * position_size
            position = trade_value // data['close'].iloc[i]
            buy_price = data['close'].iloc[i]
            balance -= position * buy_price

        # Sell signal or stop-loss/take-profit conditions
        elif (data['Signal'].iloc[i] == -1 or 
              (position > 0 and data['close'].iloc[i] <= buy_price * (1 - stop_loss)) or
              (position > 0 and data['close'].iloc[i] >= buy_price * (1 + take_profit))):
            balance += position * data['close'].iloc[i]
            position = 0  # Reset position

    # Final balance includes value of remaining shares
    final_balance = balance + (position * data['close'].iloc[-1])
    return final_balance
