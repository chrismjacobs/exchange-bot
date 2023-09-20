import os
import json
import krakenAPI as kAPI
import datetime
from settings import API_KEY_KRAKEN, API_SEC_KRAKEN, APIPATH


# accessible on your Account page under Settings -> API Keys
apiPublicKey = API_KEY_KRAKEN
# accessible on your Account page under Settings -> API Keys
apiPrivateKey = API_SEC_KRAKEN


timeout = 20
checkCertificate = True  # when using the test environment, this must be set to "False"
useNonce = False  # nonce is optional


cfPublic = kAPI.cfApiMethods(APIPATH,
                             timeout=timeout,
                             checkCertificate=checkCertificate
                             )
cfPrivate = kAPI.cfApiMethods(APIPATH,
                              timeout=timeout,
                              apiPublicKey=apiPublicKey,
                              apiPrivateKey=apiPrivateKey,
                              checkCertificate=checkCertificate,
                              useNonce=useNonce
                              )

def getFunds():
    result = cfPrivate.get_accounts()
    res = json.loads(result)
    if res['result'] and res['result'] != 'success':
        print('getFunds Error: ' + res['result'])

    print("get_accounts:\n", res['accounts'].keys())
    # dict_keys(['result', 'accounts', 'serverTime'])

    for fund in res['accounts']['flex']:
        print(fund + ': ' + str(res['accounts']['flex'][fund]))
    marginEquity = res['accounts']['flex']['marginEquity']
    collateralBasic = res['accounts']['flex']['marginEquity'] - res['accounts']['flex']['totalUnrealized']
    availableMargin = res['accounts']['flex']['availableMargin']
    return [marginEquity, collateralBasic, availableMargin]

def getInstruments(asset):
    result = cfPublic.get_instruments()
    #print("get_instruments:\n", result)
    print('getInstruments: ' + asset)
    resultDict = json.loads(result)
    for i in resultDict['instruments']:
        print(i['symbol'])
        if asset in i['symbol'] and 'pf' in i['symbol']:
            print('getInstruments: Asset Found ' + i['symbol'])
            return i['symbol']
        if asset == 'BTC':
            print('found pf_xbtusd')
            return 'pf_xbtusd'

    return None

def getTicker(instrument):

    result = cfPublic.get_tickers()
    res = json.loads(result)

    print("get_tickers:\n", res.keys())
    #  dict_keys(['result', 'tickers', 'serverTime']) # tickers is list
    if res['result'] and res['result'] != 'success':
        print('getTickers Error: ' + res['result'])

    # for t in res['tickers']:

    #     print(t['symbol'])
    #     print(t)
    #     if 'pair' in t:  # in_ and rr_ instruments have no pair value
    #         print(t['pair'])
    #         print(t['markPrice'])

    for t in res['tickers']:
        if t['symbol'] == instrument:
            print ('getTicker: \n' +  t['symbol'] + ':\n ' + str(t))
            return t['markPrice']


def tradeStatus(instrument, LEV):
    print('tradeStatus')
    result = cfPrivate.get_openpositions()
    res = json.loads(result)
    if res['result'] and res['result'] != 'success':
        print('tradeStatus Error: ' + res['result'])

    for p in res['openPositions']:
        if p['symbol'] == instrument:
            print('tradeStatus found:\n ' + instrument + ' ' + p['side'] + '\n' + str(p))
            openLEV = p['maxFixedLeverage']
            if openLEV != LEV:
                return instrument + ': Double check leverage is same as exchange'
            else:
                return p['side']

    ## no tradeStatus found
    return None

def getAllocation(instrument, PROP, LEV, OPENSIZE):

    [marginEquity, collateralBasic, availableMargin] = getFunds()
    #print(marginEquity, collateralBasic, availableMargin)
    usdCollateral = round(collateralBasic * 0.95 * int(PROP)/100)
    markPrice = getTicker(instrument)

    r = 3

    if markPrice > 1000:
        r = 2
    elif markPrice > 100:
        r = 1
    else:
        r = 0

    assetAmount = usdCollateral/markPrice * int(LEV)

    print('Allocating for ' + instrument + ':\nCollateral $' + str(collateralBasic) +  ':\nCollateral% ' + str(usdCollateral) + '\nAmount of asset on leverage: ' + str(round(assetAmount, r)))

    return round(assetAmount, r)

def getStopPrice(instrument, STOP, SIDE):
    STOPPRICE = 0.0

    markPrice = getTicker(instrument)

    STOPPRICE = markPrice - int(STOP)

    if SIDE == 'sell':
        STOPPRICE = markPrice + int(STOP)

        ## get mark price
    print('getStopPrice: ' + str(STOPPRICE))
    return STOPPRICE

def closeOpen(instrument, STOP, PROP, LEV, STOPID):
    result = cfPrivate.get_openpositions()
    res = json.loads(result)
    for p in res['openPositions']:
        if p['symbol'] == instrument:
            print('tradeStatus found:\n ' + instrument + ' ' + p['side'] + '\n' + str(p))

            CLOSESIZE = p['size']

            SIDE = None
            CLOSESIDE = None
            STOPSIDE = None

            if p['side'] == 'long':
                SIDE = 'sell'
                STOPSIDE = 'buy'
                CLOSESIDE = 'sell'
            elif p['side'] == 'short':
                SIDE = 'buy'
                STOPSIDE = 'sell'
                CLOSESIDE = 'buy'

            closeOrder = {
                "orderType": "mkt",
                "symbol": instrument,
                "side": CLOSESIDE,
                "size": CLOSESIZE
            }
            closeResult = cfPrivate.send_order_1(closeOrder)
            closeRes = json.loads(closeResult)
            print(closeRes)
            if len(closeRes['sendStatus']) < 2:
                #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
                print('closeOrder Error: ' + str(closeRes['sendStatus']))
                return {'error': closeResult, 'instrument': instrument}
            print('CLOSE POSITION:\n' + closeResult)

            ### Close last stop order
            result = cfPrivate.cancel_order(STOPID)
            print("cancel_order:\n", result)

            SIZE = getAllocation(instrument, PROP, LEV, p['size'])

            openOrder = {
                "orderType": "mkt",
                "symbol": instrument,
                "side": SIDE,
                "size": SIZE
            }
            openResult = cfPrivate.send_order_1(openOrder)
            openRes = json.loads(openResult)
            if len(openRes['sendStatus']) < 2:
                #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
                print('openOrder Error: ' + str(openRes['sendStatus']))
                return {'error': openResult, 'instrument': instrument}
            print('OPEN POSITION:\n' + openResult)

            STOPPRICE = getStopPrice(instrument, STOP, SIDE)
            STOPID = instrument + '_' + str(STOPPRICE)

            stopOrder = {
                "orderType": "stp",
                "symbol": instrument,
                "side": STOPSIDE,
                "size": SIZE,
                "stopPrice" : STOPPRICE,
                "triggerSignal": "mark_price",
                "cliOrdId": STOPID
            }

            stopResult = cfPrivate.send_order_1(stopOrder)
            stopRes = json.loads(stopResult)
            if len(stopRes['sendStatus']) < 2:
                #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
                print('stopOrder Error: ' + str(stopRes['sendStatus']))
                return {'error': stopResult, 'instrument': instrument}
            print('STOP POSITION:\n' + stopResult)
            STOPORDER = stopRes['sendStatus']['order_id']

            return {'status': 'close open stop', 'instrument': instrument, 'STOPID': STOPORDER }


def openPosition(instrument, STOP, PROP, LEV, SIDE):
    SIZE = getAllocation(instrument, PROP, LEV, None)

    STOPSIDE = 'sell'

    if SIDE == 'sell':
        STOPSIDE = 'buy'


    openOrder = {
        "orderType": "mkt",
        "symbol": instrument,
        "side": SIDE,
        "size": SIZE
    }
    openResult = cfPrivate.send_order_1(openOrder)
    openRes = json.loads(openResult)
    if len(openRes['sendStatus']) < 2:
        #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
        print('openNewOrder Error: ' + str(openRes['sendStatus']))
        return {'error': openResult, 'instrument': instrument}
    print('OPEN NEW POSITION:\n' + openResult)

    STOPPRICE = getStopPrice(instrument, STOP, SIDE)
    STOPID = instrument + '_' + str(STOPPRICE)
    stopOrder = {
        "orderType": "stp",
        "symbol": instrument,
        "side": STOPSIDE,
        "size": SIZE,
        "stopPrice" : STOPPRICE,
        "cliOrdId": STOPID
    }

    stopResult = cfPrivate.send_order_1(stopOrder)
    stopRes = json.loads(stopResult)
    if len(stopRes['sendStatus']) < 2:
        #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
        print('stopNewOrder Error: ' + stopRes['sendStatus'])
        return {'error': stopResult, 'instrument': instrument}
    print('STOP NEW POSITION:\n' + stopResult)

    STOPORDER = stopRes['sendStatus']['order_id']
    print('STOP NEW ORDER ' + STOPORDER)
    return {'status': 'START NEW POSITION', 'instrument': instrument, 'STOPID': STOPORDER }


instrument = 'pf_xbtusd'
PROP=80
LEV=5
STOP=200
STOPID= "143d2d66-c82e-49fc-8b12-117aad9127fd"
SIDE='buy'
ORDERID = "143d2d66-c82e-49fc-8b12-117aad9127fd"

# closeOpen(instrument, STOP, PROP, LEV, STOPID)
# getAllocation(instrument, PROP, LEV, None)
# result = cfPrivate.cancel_order(STOPID)
# print("cancel_order:\n", result)
# openPosition(instrument, STOP, PROP, LEV, SIDE)
#tradeStatus(instrument, 5)
# getTicker(instrument)

