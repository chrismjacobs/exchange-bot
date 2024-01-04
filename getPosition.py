from config import API_KEY, API_SECRET

from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

# print(session.get_open_orders(
#     category="inverse",
#     symbol="BTCUSD",
#     openOnly=0,
#     limit=10,
# ))

def getPosition(_sym, _cat):
    response = (session.get_positions(
        category=_cat,
        symbol=_sym,
    ))
    print(response['retMsg'])
    print(len(response['result']['list']))

    data = response['result']['list'][0]

    dataDict = {
        'side' : data['side'],
        'size' : data['size'],
        'value' : data['positionValue'],
        'price' : data['avgPrice'],
        'lev' : data['leverage'],
        'stop' : data['stopLoss'],
        'profit' : data['takeProfit'],
        'time' : data['updatedTime']
        }

    for d in dataDict:
        print(d, dataDict[d])

    print(response)
    return dataDict

def setLeverage(_sym, _cat):
    response = session.set_leverage(
        category=_cat,
        symbol=_sym,
        buyLeverage="6",
        sellLeverage="6",
    )

def getHiLo(_sym, _cat):
    START = getPosition(_sym, _cat)['time']
    response = session.get_kline(
        category=_cat,
        symbol=_sym,
        interval='5',
        #start=int(START)
    )

    print(len(response))

    candleList = response['result']['list']

    print(candleList)

    high = 0
    low = 100000000000

    for c in candleList:
        _high = float(c[2])
        _low = float(c[3])
        if _high > high:
            high = _high
        if _low < low:
            low = _low

    print(high, low)



getPosition('BTCUSD', 'inverse')
getHiLo('BTCUSD', 'inverse')

## setLeverage('MATICUSDT', 'linear')