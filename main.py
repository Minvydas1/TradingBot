import websocket
import json
from datetime import datetime
import requests 
from binance.client import Client
from binance.enums import *
import config
import pushbullet
from currency_converter import CurrencyConverter
from keep_alive import keep_alive
import os
from replit import db
import pprint


#DON'T FORGET TO UPDATE SOCKET IF YOU WANT TO MAKE CHANGES!
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"

STOCH_OVERBOUGHT = 60
#MINIMUM 10$
TRADE_QUANTITY = 0.00021
TRADE_QUANTITY_SELL = 0.00021
TRADE_SYMBOL = 'BTCUSDT'
PARAMS_SYMBOL = 'BTC/USDT'
INTERVAL = '15m'
PERCENT = 1
POSITIVE_PERCENT = 0.5
p = False
NEGATIVE_PERCENT = -1
n1 = False
NEGATIVE_PERCENT2 = -3
n2 = False
NEGATIVE_PERCENT3 = -5
n3 = False
NEGATIVE_PERCENT4 = -10
n4 = False

client = Client(config.API_KEY, config.API_SECRET)

closes = []

#Variables for database
date_format = 'dd/mm/yy hh:mm'

pb = pushbullet.PushBullet(config.API_PUSH)

c = CurrencyConverter()

#BINANCE ORDER
def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def on_open(ws):
    db["position"] = 0
    print('opened connection')

def on_close(ws):
    print("closed connection")

def on_message(ws, message):

    #VARIABLES
    global closes, row, p, n1, n2, n3, n4, in_position

    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    print(close)
    print(is_candle_closed)

    in_position = db["position"]
    print(in_position)

    # GET STOCHRSI INDICATOR
    indicator = "stochrsi"
  
    endpoint = f"https://api.taapi.io/{indicator}"
  
    parameters = {
        'secret': config.API_TA,
        'exchange': 'binance',
        'symbol': PARAMS_SYMBOL,
        'interval': INTERVAL,
        'kPeriod': '3'
        } 
  
    response = requests.get(url = endpoint, params = parameters)
  
    result = response.json() 

    fast_dstr = result['valueFastD']

    fast_d = float(fast_dstr)
    print("fast d is: {}".format(fast_d))

    # GET MACD INDICATOR
    indicator = "macd"
  
    endpoint = f"https://api.taapi.io/{indicator}"
  
    parameters = {
        'secret': config.API_TA,
        'exchange': 'binance',
        'symbol': PARAMS_SYMBOL,
        'interval': INTERVAL,
        'optInFastPeriod':'7',
        'optInSlowPeriod':'23',
        'optInSignalPeriod':'10'
        } 
  
    response = requests.get(url = endpoint, params = parameters)
  
    result = response.json() 

    macdstr = result['valueMACD']
    signal_macdstr = result['valueMACDSignal']
    macd = float(macdstr)
    signal_macd = float(signal_macdstr)

    print("macd is: {}".format(macd))
    print("signal macd is: {}".format(signal_macd))
        
    if fast_d < STOCH_OVERBOUGHT:
        if macd > signal_macd:
            if macd < 0.002:
                if in_position == 0:
                    print("________________BUY BUY BUY!__________________")
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        db["position"] = 1

                        #ADD CRYPTO PRICE TO A LIST
                        json_message = json.loads(message)
                        candle = json_message['k']
                        close = candle['c']
                        closes.append(float(close))
                        print(closes)
                        bought_push = float(closes[-1])

                        #PUSHING NOTIFICATION
                        pb.push_note('BUY order filled', 'Crypto was bought at: {}$'.format(bought_push))
                    else:
                        print("BUY ORDER did not succeed!")
                        
                else:
                    print("MACD CROSSED SIGNAL, BUT YOU ARE ALREADY IN POSITION")
            else:
                print("MACD CROSSED SIGNAL, BUT IT'S TOO RISKY")

    if in_position == 1:
        #GETTING CRYPTO BOUGHT AND SOLD PRICE
        json_message = json.loads(message)
        candle = json_message['k']
        close = candle['c']
        bought = float(closes[-1])
        current = float(close)
        print("Current price at: {}".format(current))
        print("Bought at: {}".format(bought))

        #CALCULATING PROFIT PERCENT
        profit = current - bought
        calculation = profit*100/current
        percent = round(calculation, 2)
        print("YOU ARE IN POSITION")
        print("Percent is: {}".format(percent))
        dollars = bought * TRADE_QUANTITY

        #TAKING PROFITS
        if fast_d > STOCH_OVERBOUGHT:
            if percent > PERCENT:   
                print("_________________SELL SELL SELL!__________________")
                order_succeeded = order(SIDE_SELL, TRADE_QUANTITY_SELL, TRADE_SYMBOL)
                if order_succeeded:
                    db["position"] = 0

                    #CALCULATING PROFIT AFTER TAXES
                    after_tax = percent - 0.15
                    tax = round(after_tax, 2)
                    print("Percent is: {}%".format(after_tax))

                    #CALCULATING PROFIT IN EURO
                    converter = c.convert(dollars, 'EUR', 'USD')
                    euro_profit = converter * after_tax / 100
                    euro = round(euro_profit, 2)
                    print("Profit in euro: {}€".format(euro))

                    #PUSHING NOTIFICATION
                    pb.push_note('SELL order filled', 'Crypto was sold for: {}% profit'.format(tax))

                    date_time = datetime.now()
                    x = date_time.strftime("%Y-%m-%d")

                    db["date"] = x
                    db["percent"] = tax
                    db["euro"] = euro
                    db["profit/loss"] = "Profit"
                else:
                    print("SELL ORDER did not succeed!")

        #INFORMING ABOUT POSITION 
        if percent >= POSITIVE_PERCENT:
            if p == False:
                pb.push_note('Crypto price RAISING', '0.5%')
                p = True
        elif percent <= NEGATIVE_PERCENT:
            if n1 == False:
                pb.push_note('Crypto price DROPPING', '-1%')
                n1 = True

                p = False
                n2 = False
                n3 = False
                n4 = False
        elif percent <= NEGATIVE_PERCENT2:
            if n2 == False:
                pb.push_note('Crypto price DROPPING','-3%')
                n2 = True

                p = False
                n1 = False
                n3 = False
                n4 = False
        elif percent <= NEGATIVE_PERCENT3:
            if n3 == False:
                pb.push_note('Crypto price DROPPING','-5%')
                n3 = True

                p = False
                n1 = False
                n2 = False
                n4 = False
        elif percent <= NEGATIVE_PERCENT4:
            if n4 == False:
                pb.push_note('Crypto price DROPPING','-10%')
                n4 = True

                p = False
                n1 = False
                n2 = False
                n3 = False
    
    else:
        print("YOU ARE NOT IN THE POSITION")
    
keep_alive()
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()