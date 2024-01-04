from settings import API_KEY, API_SECRET

from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

def getCat(_sym):
    _cat = 'inverse'
    if 'USDT' in _sym:
        _cat = 'linear'
    return _cat

def getOrders(_sym):
    _cat = getCat(_sym)

    response = (session.get_open_orders(
        category=_cat,
        symbol=_sym,
    ))
    ok = response['retMsg']
    print(f'getOrders {ok}')
    #print(response['result'])

    data = response['result']['list']

    if len(data) == 0:
        print(f'No orders on {_sym}')
        return False

    return True

def getPosition(_sym):
    _cat = getCat(_sym)

    response = (session.get_positions(
        category=_cat,
        symbol=_sym,
    ))
    ok = response['retMsg']
    print(f'getPosition {ok}')
    #print(f'getPosition {str(response['retMsg'])}')

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

    if int(dataDict['value']) == 0:
        print(f'No positions on {_sym}')
        return False

    for d in dataDict:
        print(d, dataDict[d])

    #print(response)
    return dataDict

def setLeverage(_sym):
    _cat = getCat(_sym)

    response = session.set_leverage(
        category=_cat,
        symbol=_sym,
        buyLeverage="6",
        sellLeverage="6",
    )

def checkValid(_sym):
    _cat = getCat(_sym)

    if getPosition(_sym):
        print(f'No Trade Action: Positions on {_sym}')
        return False
    elif getOrders(_sym):
        print(f'No Trade Action: Orders on {_sym}')
        return False
    else:
        return True

def getHL(side, current, stop, mode):

    now = datetime.now()
    minutes = 5
    timestamp = int(datetime.timestamp(now)) - int(minutes)*60
    data = session.query_kline(symbol="BTCUSD", interval="1", from_time=str(timestamp))['result']

    hAry = []
    lAry = []

    for i in range(0, len(data)):
        hAry.append(int(data[i]['high'].split('.')[0]))
        lAry.append(int(data[i]['low'].split('.')[0]))

    mHi = max(hAry)
    mLow = min(lAry)

    if side == 'Buy':
        distance = abs(current - mLow)
        if distance > stop:
            stop_loss = current - stop
        else:
            stop_loss = mLow - 45

    if side == 'Sell':
        distance = abs(current - mHi)
        if distance > stop:
            stop_loss = current + stop
        else:
            stop_loss = mHi + 45


    return stop_loss


def setLeverage(_sym, _entry, _stop, _risk):
    _cat = getCat(_sym)

    diff = abs(_entry - _stop)
    per = (diff/_entry)*100

    _lev = round(_risk/per, 1)
    if _lev > 10:
        print(f'set lev on {_sym} at {_lev} : Lev too high')
        return False

    try:
        response = session.set_leverage(
            category=_cat,
            symbol=_sym,
            buyLeverage=str(_lev),
            sellLeverage=str(_lev),
        )
        ok = response['retMsg']
        print(f'set lev on {_sym} at {_lev} : {ok}')

        if ok == 'OK':
            return _lev
        else:
            return False

    except:
        print(f'set lev on {_sym} at {_lev} : Not modified')
        return _lev



    else:
        return False


def getQty(_sym, _amt, _lev, _entry):
    _cat = getCat(_sym)

    data = session.get_tickers(
        category=_cat,
        symbol=_sym,
        )

    info = session.get_instruments_info(
        category=_cat,
        symbol=_sym,
    )
    qtyStep = info['result']['list'][0]['lotSizeFilter']['qtyStep']

    last_entry = float(data['result']['list'][0]['lastPrice'])
    print(last_entry)

    if _entry == 0:
        _entry = last_entry

    qty = (_amt / _entry) * _lev



    rQty = round(qty, 1)
    if float(qtyStep) == 0.001:
        rQty = round(qty, 3)
    elif float(qtyStep) == 0.01:
        rQty = round(qty, 2)

    print(f'QTY: {_amt} / {_entry} / {_lev} / {qtyStep} / {rQty}')

    return rQty

def placeOrder(_sym,_type, _side, _entry, _amt, _stop, _profit, _risk):
    _cat = getCat(_sym)

    if not checkValid(_sym):
        return False

    _lev = setLeverage(_sym, _entry, _stop, _risk)

    if _lev:
        _qty = getQty(_sym, _amt, _lev, _entry)
    else:
        return False

    _pidx = 1
    if _side == 'Sell':
        _pidx = 2

    try:

        response = session.place_order(
                category=_cat,
                symbol=_sym,
                side=_side,
                orderType=_type,
                qty=_qty,
                price=_entry,
                stopLoss=_stop,
                takeProfit=_profit,
                positionIdx=_pidx
            )

        return response

    except Exception as e:
        return str(e)


# getPosition('ALGOUSDT')

# getOrders('ALGOUSDT')

# print(getQty('ALGOUSDT', 100, 5))
assDict = {
    1 : 'ALGOUSDT',
    2 : 'ALICEUSDT',
    3 : 'AVAXUSDT',
    4 : 'BANDUSDT',
    5 : 'BTCUSDT',
    6 : 'ETHUSDT',
    7 : 'MATICUSDT',
    8 : 'NEARUSDT'
}

symx = 5
_sym = assDict[symx]
_side = 'Sell'
_type = 'Limit'
_entry = 2393
_stop = 2403
_profit = 2381
_amt = 100
_risk = 4

# placeOrder(_sym,_type, _side, _entry, _amt, _stop, _profit, _risk)


getQty(_sym, _amt, 3.6, 0)

## setLeverage('MATICUSDT', 'linear')