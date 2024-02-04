from datetime import datetime
from binance.client import Client
from pprint import pprint
import time
import keys
import pygame


client = Client(keys.API_KEY, keys.SECRET_KEY, testnet=True)

HOUR = Client.KLINE_INTERVAL_1HOUR
MINUTE = Client.KLINE_INTERVAL_1MINUTE


def play_sound(file_path):
    pygame.mixer.init()
    pygame.mixer.set_num_channels(0)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    pygame.time.delay(5000)


def get_kline(asset, hours_back=0):
    try:
        if hours_back:
            current_time = int(datetime.now().timestamp() * 1000) - 60_000
            kline = client.get_klines(symbol=asset, interval=MINUTE, startTime=current_time - (3600000 * hours_back), limit=1)
        else:
            kline = client.get_klines(symbol=asset, interval=MINUTE, limit=1)
        if not kline:
            raise Exception("No data returned from Binance API.")
        
        stamp, open_price, high_price, low_price, close_price, volume = [round(float(i), 3) for i in kline[0][:6]]
        dt = datetime.fromtimestamp(stamp / 1_000)
        result = {"time": dt, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume}
        return result
    
    except Exception as ex:
        print(f"Error fetching data from Binance API: {ex}")


def print_accaunt(assets):
    account_info = client.get_account()
    for balance in account_info['balances']:
        if balance['asset'] in assets:
            print(f"{balance['asset']}: {balance['free']}")



def strategy(asset, buy_amount, buy_limit, sell_limit, leverage, buy_percent):
    try:
        current_kline, hour_ago_kline = get_kline(asset), get_kline(asset, hours_back=1)

        # =========================================================================================
        print('=' * 50)
        print(f"First checkpoint:")
        print(f"\tFirst if:                 {hour_ago_kline['close'] * (1 - buy_limit) >= current_kline['close']}")
        print(f"\tActual time:              {datetime.now()}")
        print(f"\tTime of current kline:    {current_kline['time']}")
        print(f"\tCurrent price:            {current_kline['close']}")
        print(f"\tHour ago price:           {hour_ago_kline['close']}")
        # =========================================================================================
        price_difference_percent = round(abs((current_kline['close'] / hour_ago_kline['close'] * 100) - 100), 3)
        if current_kline['close'] > hour_ago_kline['close']:
            print(f"\tCurrent close is larger: {price_difference_percent}%")
        else:
            print(f"\tCurrent close is lower: {price_difference_percent}%")
        # =========================================================================================


        # First if
        if hour_ago_kline['close'] * (1 - buy_limit) >= current_kline['close']:
            qty = round((buy_amount * leverage * buy_percent) / current_kline['close'], 4)
            
            # BUY ORDER
            buy_order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity=qty)
            buy_price = float(buy_order['fills'][0]['price'])
            
            # =========================================================================================
            print('=' * 50)
            print(f"\tSecond checkpoint:")
            print(f"\t\tBuy price:   {buy_price}")
            print(f"\t\tQuantity:    {qty}")
            print(f"\t\tTotal price: {qty * buy_price}")
            # =========================================================================================

            while True:
                ticker = client.get_ticker(symbol=asset)
                current_price = float(ticker['lastPrice'])

                # =========================================================================================
                print('=' * 50)
                print(f"\t\tWhile cycle:")
                print(f"\t\t\tActual time:    {datetime.now()}")
                print(f"\t\t\tCurrent price:  {current_price}")
                print(f"\t\t\tGoal price:     {round(buy_price * (1 + sell_limit), 3)}")
                print(f"\t\t\tWhile if        {buy_price * (1 + sell_limit) <= current_price}")
                # ========================================================================================
                price_difference_percent = round(abs(current_price / buy_price * 100 - 100), 3)
                if buy_price > current_price:
                    print(f"\t\t\tBuy price is larger for: {price_difference_percent}%")
                else:
                    print(f"\t\t\tBuy price is lower for:  {price_difference_percent}%")
                # =========================================================================================

                # Second if
                if buy_price * (1 + sell_limit) <= current_price:
                    
                    # SELL ORDER
                    sell_order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity=qty, newOrderRespType='RESULT')
                    
                    print(f"sell order has completed")
                    pprint(sell_order)
                    return True

                time.sleep(5)
                
            
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    ASSET = 'ETHUSDT'
    
    
    BUY_LIMIT = 0.01
    SELL_LIMIT = 0.0125

    LEVERAGE = 10
    BUY_PERCENT = 0.85
    BUY_AMOUNT = 1000
        
    [print('/' * 50) for _ in range(3)]
    
    # sell_order = client.create_order(symbol=ASSET, side='SELL', type='MARKET', quantity=14.08580000, newOrderRespType='RESULT')
    print_accaunt(['USDT', 'ETH'])
    print(f"BUY_LIMIT: {BUY_LIMIT * 100}%")
    print(f"SELL_LIMIT: {SELL_LIMIT * 100}%")

    continue_strategy = True
    while continue_strategy:
        while datetime.utcnow().second != 0:
            time.sleep(1)
        strategy_reuslt = strategy(ASSET, BUY_AMOUNT, BUY_LIMIT, SELL_LIMIT, LEVERAGE, BUY_PERCENT)
        time.sleep(60)

    print('Strategy is completed')
    print_accaunt(['USDT', 'ETH'])
    play_sound('sound.wav')