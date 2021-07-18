import websocket as ws, json, pprint, numpy as np, talib
from binance.client import Client
from binance.enums import *
import config

closes = []

# Websocket connected to binance stream for eth over 1m interavls
sokt = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

# Rsi period of 14, RSI>70 is overbought, RSI<30 is oversold
RSI_PD = 14
RSI_OVERB = 70
RSI_OVERS = 30
    
# Plan to trade eth in .005ETH increments
SYMB = 'ETHUSD'
QUANT = 0.005

# Boolean value to store whether or not we are currently in a position
in_pos = False

# Client obtained using binance api
client = Client(config.API_KEY, config.API_SECRET, tld='us')

# Order function using a try catch to make sure order successfully executes, uses binance create_order method
def order(symbol, quantity, side, order_type=ORDER_TYPE_MARKET):
    try:
        print("placing order")
        order = client.create_test_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        print(order)
    except Exception as e:
        return False

    return True
    
# Notifies when connection to stream opens
def on_open(webs):
    print("opened connection")
    
# Notifies when connection to stream closes
def on_close(webs):
    print("closed connection")

# Notifies when incoming message comes from stream
def on_message(webs, msg):
    # Need to update global closes array
    global closes

    # Receives message from stream in json format
    json_msg = json.loads(msg)
    
    candle = json_msg['k'] #k holds all market data

    is_closed = candle['x'] #Is true only for the final message from the candle stick
    close = candle['c'] #Gives closing price

    # If we have received the end of a candle stick
    if is_closed:
        print(f'Candle closed {close}')
        closes.append(float(close))
        print("closes")
        print(closes)

        # If we receive enough RSI values for our RSI_PD
        if len(closes) > RSI_PD:
            # Calculate rsi thus far
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes, RSI_PD)
            print("rsi's calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print(f"the current rsi is {last_rsi}")

            if last_rsi > RSI_OVERB:
                if in_pos:
                    print("sell")
                    order_success = order(SYMB, QUANT, SIDE_SELL)
                    if order_success:
                        in_pos = False
                else:
                    print('we dont own any to sell')
            
            if last_RSI < RSI_OVERS:
                if in_pos:
                    print("is oversold, already own it")
                else:
                    print("Buy")
                    order_success = order(SYMB, QUANT, SIDE_BUY)
                    if order_success:
                        in_pos = True

webs = ws.WebSocketApp(sokt, on_open=on_open, on_close=on_close, on_message=on_message)
webs.run_forever()

    


