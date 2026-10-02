# daily k

def calculate_pct_chg(buy_price, sell_price):
    if buy_price == 0:
        return 0
    return (sell_price - buy_price) / buy_price * 100


def predict_buy_price(df, days=5):
    if df.empty or len(df) < days:
        return None
    recent_low = df.tail(days)['low'].min()
    return recent_low


def predict_sell_price(df, days=5):
    if df.empty or len(df) < days:
        return None
    recent_high = df.tail(days)['high'].max()
    return recent_high



# simulate trading
def simulate_trading(df, duration_days=182):
    # sort the dataframe by date in ascending order

    # trade window 
    # predict buy price based on the last 5 days low
    # predict sell price based on the last 5 days high
    # if the current price is lower than the predicted buy price, buy
    # if the current price is higher than the predicted sell price, sell
    # calculate the profit/loss percentage for each trade
    # return the total profit/loss percentage over the duration_days
    if df.empty or len(df) < duration_days:
        return None
    pass
