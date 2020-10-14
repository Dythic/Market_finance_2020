#!/usr/bin/env python3

import fxcmpy
import time
import datetime as dt
import pyti.bollinger_bands as bb
from pyti.directional_indicators import average_directional_index as adx

token = '572413a650c252f66e0501cf79fc5069922d0e73'
symbol = 'EUR/USD'
timeframe = 'm5'
bb_periods = 20
bb_standard_deviations = 2.0
adx_periods = 14
adx_trade_below = 25
amount = 10

pricedata = None
numberofcandles = 300

con = fxcmpy.fxcmpy(access_token=token)

def Prepare():
    global pricedata

    print("Requesting Initial Price Data...")
    pricedata = con.get_candles(symbol, period=timeframe, number=numberofcandles)
    print(pricedata)
    print("Initial Price Data Reveived")

def StrategyHeartBeat():
    while True:
        currenttime = dt.datetime.now()
        if timeframe == "m1" and currenttime.second == 0 and getLastestPriceData():
            Update()
        elif timeframe == "m5" and currenttime.second == 0 and currenttime.minute % 5 == 0 and getLastestPriceData():
            Update()
            time.sleep(240)
        elif timeframe == "m15" and currenttime.second == 0 and currenttime.minute % 15 == 0 and getLastestPriceData():
            Update()
            time.sleep(840)
        elif timeframe == "m30" and currenttime.second == 0 and currenttime.minute % 30 == 0 and getLastestPriceData():
            Update()
            time.sleep(1740)
        elif currenttime.second == 0 and currenttime.minute == 0 and getLastestPriceData():
            Update()
            time.sleep(3540)
        time.sleep(1)

def getLastestPriceData():
    global pricedata

    new_pricedata = con.get_candles(symbol, period=timeframe, number=numberofcandles)
    if new_pricedata.index.values[len(new_pricedata.index.values) - 1] != pricedata.index.values[len(new_pricedata.index.values) - 1]:
        pricedata = new_pricedata
        return True

    counter = 0
    while new_pricedata.index.values[len(new_pricedata.index.values) - 1] == pricedata.index.values[len(new_pricedata.index.values) - 1] and counter < 3:
        counter += 1
        time.sleep(10)
        new_pricedata = con.get_candles(symbol, period=timeframe, number=numberofcandles)
    if new_pricedata.index.values[len(new_pricedata.index.values) - 1] != pricedata.index.values[len(new_pricedata.index.values) - 1]:
        pricedata = new_pricedata
        return True
    else:
        return False

def Update():
    print(str(dt.datetime.now()) + " " + timeframe + " Bar Closed - Running Update Function ...")

    iBBUpper = bb.upper_bollinger_band(pricedata['bidclose'], bb_periods, bb_standard_deviations)
    iBBMiddle = bb.middle_bollinger_band(pricedata['bidclose'], bb_periods, bb_standard_deviations)
    iBBLower = bb.lower_bollinger_band(pricedata['bidclose'], bb_periods, bb_standard_deviations)
    iADX = adx(pricedata['bidclose'], pricedata['bidhigh'], pricedata['bidlow'], adx_periods)

    close_price = pricedata['bidclose'][len(pricedata)-1]
    BBUpper = iBBUpper[len(iBBUpper)-1]
    BBMiddle = iBBMiddle[len(iBBMiddle)-1]
    BBLower = iBBLower[len(iBBLower)-1]
    ADX = iADX[len(iADX)-1]

    print("Close Price: " + str(close_price))
    print("Upper BB: " + str(BBUpper))
    print("Middle BB: " + str(BBMiddle))
    print("Lower BB: " + str(BBLower))
    print("ADX: " + str(ADX))
    
    if countOpenTrades()>0:
        openpositions = con.get_open_positions(kind='list')
        for position in openpositions:
            if position['currency'] == symbol:
                print("Changing Limit for tradeID: " + position['tradeId'])
                try:
                    editlimit = con.change_trade_stop_limit(trade_id=position['tradeId'], is_stop=False, rate=BBMiddle, is_in_pips=False)
                except:
                    print("	  Error Changing Limit.")
                else:
                    print("	  Limit Changed Successfully.")

    if ADX < adx_trade_below:
        if countOpenTrades("B") == 0 and close_price < BBLower: 
            print(" BUY SIGNAL!") 
            print(" Opening Buy Trade...") 

            stop = pricedata['askclose'][len(pricedata)-1] - (BBMiddle - pricedata['askclose'][len(pricedata)-1]) 
            limit = BBMiddle 
            enter("B", stop, limit) 

            if countOpenTrades("S") == 0 and close_price > BBUpper:
                print("	  SELL SIGNAL!")
                print("	  Opening Sell Trade...")
                stop = pricedata['bidclose'][len(pricedata)-1] + (pricedata['bidclose'][len(pricedata)-1] - BBMiddle)
                limit = BBMiddle
                enter("S", stop, limit)
        
    if countOpenTrades("B") > 0 and close_price > BBMiddle:
        print("	  Closing Buy Trade(s)...")
        exit("B")
    if countOpenTrades("S") > 0 and close_price < BBMiddle:
        print("	  Closing Sell Trade(s)...")
        exit("S")

    print(str(dt.datetime.now()) + " " + timeframe + " Update Function Completed.\n")

def enter(BuySell, stop, limit):
    direction = True
    if BuySell == "S":
        direction = False
    try:
        opentrade = con.open_trade(symbol=symbol, is_buy=direction, amount=amount, time_in_force="GTC", order_type='AtMarket', is_in_pips=False, limit=limit, stop=stop)
    except:
        print("   Error Opening Trade.")
    else:
        print("   Trade Opened Successfully")

def exit(BuySell=None):
    openpositions = con.get_open_positions(kind='list')
    isbuy = True
    if BuySell == "S":
        isbuy = False
    for position in openpositions:
        if position['currency'] == symbol:
            if BuySell is None or position['isBuy'] == isbuy:
                print("   Closing tradeID: " + position['tradeId'])
                try:
                    print("   Closing tradeID: " + position['tradeId'], amount=position['amountK'])
                except:
                    print("   Error Closing Trade.")
                else:
                    print("   Trade Closed Successfully.")

def crossesOver(stream1, stream2):
    if isinstance(stream2, int) or isinstance(stream2, float):
        if stream1[len(stream1) - 1] <= stream2:
            return False
        else:
            if stream1[len(stream1) - 2] > stream2:
                return False
            elif stream1[len(stream1) - 1] < stream2:
                return True
            else:
                x = 2
                while stream1[len(stream1) - x] == stream2:
                    x = x + 1
                if stream1[len(stream1) - x] < stream2:
                    return True
                else:
                    return False
    else:
        if stream1[len(stream1) - 1] <= stream2[len(stream2) - 1]:
            return False
        else:
            if stream1[len(stream1) - 2] > stream2[len(stream2) - 2]:
                return False
            elif stream1[len(stream1) - 2] < stream2[len(stream2) - 2]:
                return True
            else:
                x = 2
                while stream1[len(stream1) - x] == stream2[len(stream2) - x]:
                    x = x + 1
                if stream1[len(stream1) - x] < stream2[len(stream2) - x]:
                    return True
                else:
                    return False

def crossesUnder(stream1, stream2):
    if isinstance(stream2, int) or isinstance(stream2, float):
        if stream1[len(stream1) - 1] >= stream2:
            return False
        else:
            if stream1[len(stream1) - 2] < stream2:
                return False
            elif stream1[len(stream1) - 1] > stream2:
                return True
            else:
                x = 2
                while stream1[len(stream1) - x] == stream2:
                    x = x + 1
                if stream1[len(stream1) - x] > stream2:
                    return True
                else:
                    return False
    else:
        if stream1[len(stream1) - 1] >= stream2[len(stream2) - 1]:
            return False
        else:
            if stream1[len(stream1) - 2] < stream2[len(stream2) - 2]:
                return False
            elif stream1[len(stream1) - 2] > stream2[len(stream2) - 2]:
                return True
            else:
                x = 2
                while stream1[len(stream1) - x] == stream2[len(stream2) - x]:
                    x = x + 1
                if stream1[len(stream1) - x] > stream2[len(stream2) - x]:
                    return True
                else:
                    return False

def countOpenTrades(BuySell=None):
    openpositions = con.get_open_positions(kind='list')
    isbuy = True
    counter = 0
    if BuySell == "S":
        isbuy = False
    for position in openpositions:
        if position['currency'] == symbol:
            if BuySell is None or position['isBuy'] == isbuy:
                counter += 1
    return counter


Prepare()
StrategyHeartBeat()