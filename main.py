from binance.client import Client
from datetime import datetime
import pytz
import time
import keys


client = Client(keys.api_key, keys.secret_key)
asset = 'BTCUSDT'
interval_hour = Client.KLINE_INTERVAL_1HOUR

round_precision = 2
# Rounding when calculating the amount of an asset to buy
# Too high accuracy can cause errors, as the exchange will not be able to process it

PATTERN = "%d.%m.%y %H:%M"

def get_candles(kline_symbol, kline_interval, kline_limit=1):
    klines = client.get_klines(symbol=asset, interval=interval_hour, limit=kline_limit)
    stamp, open_price, high_price, low_price, close_price, volume = [round(float(i), 3) for i in klines[0][:6]]
    dt = datetime.fromtimestamp(stamp / 1_000)
    result = {"date_time": dt, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume}
    return result


def get_current_price(kline_symbol):
    ticker = client.get_symbol_ticker(symbol=kline_symbol)
    current_price = round(float(ticker['price']), 3)
    return current_price


def strategy(buy_amt, SL=0.985, Target=1.02, open_position=False):
    # SL - Stop Loss 1.5%
    try:
        klines = get_candles(asset, interval_hour)
        qty = round(buy_amt / klines['close'], round_precision)     # quantity
        
        # ================================================
        open_position = True    # There must be logic here
        # ================================================

        print('point 1')
        if open_position:
            order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity=qty)
            buy_price = float(order['fills'][0]['price'])
            
            print(f"Time for candles: {klines['date_time'].strftime(PATTERN)}")
            print(f"Actual time: {datetime.now().strftime(PATTERN)}")
            print(f'Symbol: {asset}')
            print(f"Price: {klines['close']}")
            print(f"Target: {buy_price * Target}")
            print(f"Stop: {buy_price * SL}")

    except Exception as err:
        print(f"Exception: {err} at {datetime.now()}")
    else:
        flag = True
        while flag:
            time.sleep(60)
            current_price = get_current_price(asset)
            if current_price <= buy_price * SL or current_price >= buy_price * Target:
                order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity=qty)
                print(order)
                flag = False    


if __name__ == '__main__':
    print("Program has started")
    
    while True:
        if datetime.now().minute == 0:
            strategy(1)
        print(f'Time: {datetime.now().strftime(PATTERN)}')
        time.sleep(60)
        