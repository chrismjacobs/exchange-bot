from time import sleep
import math
from pybit import inverse_perpetual
from meta import r
import json


def updateStream(vol, oi, price, time):
    stream = json.loads(r.get('stream'))
    stream['lastTime'] = time
    stream['lastPrice'] = price
    stream['lastOI'] = oi
    stream['lastVol'] = vol
    r.set('stream', json.dumps(stream) )


def handle_trade_message(msg):
    # print(msg['data'])
    block = 1000000
    # deltaTotal = json.loads(r.get('deltaTotal'))
    delta = json.loads(r.get('delta')) ## reset after each volume block

    newTradeList = []
    tradeListTotal = 0

    for t in delta['tradeList']:
        tradeListTotal += t['size']


    for x in msg['data']:
        if tradeListTotal + x['size'] <= block:
            delta['tradeList'].append( { 'side' : x['side'] , 'size' : x['size'] , 'time' : x['trade_time_ms']} )
        elif len(newTradeList) == 0:
            lefttoFill = block - tradeListTotal
            carryOver = x['size'] - lefttoFill
            delta['tradeList'].append( { 'side' : x['side'] , 'size' : lefttoFill, 'time' : x['trade_time_ms']} )
            newTradeList.append({ 'side' : x['side'] , 'size' : carryOver, 'time' : x['trade_time_ms']} )
        else:
            newTradeList.append({ 'side' : x['side'] , 'size' : x['size'], 'time' : x['trade_time_ms']} )

    if len(newTradeList) > 0:
        stream = json.loads(r.get('stream'))
        time = stream['lastTime']
        price = stream['lastPrice']
        oi = stream['lastOI']
        vol = stream['lastVol']

        buyCount = 0
        sellCount = 0

        for d in delta['tradeList']:
            if d['side'] == 'Buy':
                buyCount += d['size']
            else:
                sellCount += d['size']

        newCandle = {
            'time' : time,
            'close' : price,
            'buys' : buyCount,
            'sells' : sellCount,
            'delta' : buyCount - sellCount,
            'total' : buyCount + sellCount,
            'oi': oi,
            'vol' : vol
        }

        delta['flow'][len(delta['flow']) + 1] = newCandle

        delta['tradeList'] = newTradeList

        r.set('delta', json.dumps(delta) )


    print('Delta', delta)
    r.set('delta', json.dumps(delta) )
    # r.set('deltaTotal', json.dumps(deltaTotal) )


def handle_info_message(msg):

    vol = msg['data']['total_volume']
    oi = msg['data']['open_interest']
    price = msg['data']['last_price']
    time = msg['timestamp_e6']

    updateStream(vol, oi, price, time)

# To subscribe to multiple symbols,
# pass a list: ["BTCUSD", "ETHUSD"]
def webSockets():
    openWhile =  r.get('while')
    ws_inverseP = inverse_perpetual.WebSocket(
        test=False,
        ping_interval=30,  # the default is 30
        ping_timeout=10,  # the default is 10
        domain="bybit"  # the default is "bybit"
    )

    ws_inverseP.trade_stream(
        handle_trade_message, "BTCUSD"
    )

    ws_inverseP.instrument_info_stream(
        handle_info_message, "BTCUSD"
    )
    while openWhile == 'true':
        sleep(0.1)

    return True

def runStream():
    rDict = {
        'volDaily': 153532012,
        'volOpen': 2902783986517,
        'volRec' : 0,   ### volume check at last package
        'volCount' : 0,  ### cumulative volume from stream start
        'blockCount' : 0,
        'OIRec' : 0,
        'OICount' : 0,
        'lastPrice' : 0,
        'lastTime' : 0,
        'lastOI' : 0,
        'lastVol' : 0,
    }

    dDict = {
        'tradeList' : [],
        'flow' : {}
    }

    r.set('stream', json.dumps(rDict) )
    r.set('delta', json.dumps(dDict) )
    r.set('while', 'true')
    # r.set('deltaTotal', json.dumps(dDict) )

    webSockets()

runStream()
