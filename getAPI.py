import os
import json
import krakenAPI as kAPI
from datetime import datetime
from settings import API_KEY_KRAKEN, API_SEC_KRAKEN, APIPATH
import logging

loggerAPI = logging.getLogger(__name__)
handler = logging.StreamHandler()
loggerAPI.addHandler(handler)
loggerAPI.setLevel(logging.DEBUG)
loggerAPI.debug('Test Logger API')



# accessible on your Account page under Settings -> API Keys
apiPublicKey = API_KEY_KRAKEN
# accessible on your Account page under Settings -> API Keys
apiPrivateKey = API_SEC_KRAKEN

documentation = 'https://docs.futures.kraken.com/'

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
        loggerAPI.warning('getFunds Error: ' + res['result'])

    # loggerAPI.info("get_accounts:\n" + str(res['accounts'].keys()))
    # dict_keys(['result', 'accounts', 'serverTime'])

    for fund in res['accounts']['flex']:
        loggerAPI.debug(fund + ': ' + str(res['accounts']['flex'][fund]))
    marginEquity = res['accounts']['flex']['marginEquity']
    collateralBasic = res['accounts']['flex']['marginEquity'] - res['accounts']['flex']['totalUnrealized']
    availableMargin = res['accounts']['flex']['availableMargin']
    return [round(marginEquity), round(collateralBasic), round(availableMargin)]


def getInstruments(asset):
    result = cfPublic.get_instruments()
    #loggerAPI.info("get_instruments:\n", result)
    loggerAPI.info('getInstruments: ' + asset)
    resultDict = json.loads(result)
    if 'instruments' in resultDict:
        for i in resultDict['instruments']:
            # loggerAPI.info(i['symbol'])
            if asset.lower() in i['symbol'] and 'pf' in i['symbol']:
                loggerAPI.info('getInstruments: Asset Found ' + i['symbol'])
                return i['symbol']
            if asset == 'BTC':
                loggerAPI.info('found pf_xbtusd')
                return 'PF_XBTUSD'
    else:
        loggerAPI.info('getInstruments Error: ' + asset + ':\n' + result)

    return None

def getTicker(instrument):

    result = cfPublic.get_tickers()
    res = json.loads(result)

    loggerAPI.info("get_tickers: " + instrument + ' ' + str(res.keys()))
    #  dict_keys(['result', 'tickers', 'serverTime']) # tickers is list
    if res['result'] and res['result'] != 'success':
        loggerAPI.info('getTickers Error: ' + res['result'])

    for t in res['tickers']:
        ## loggerAPI.warning('TICKERS ' + t['symbol'] + str(t['symbol'] == instrument))
        if t['symbol'].upper() == instrument.upper():
            ### symbols appear as lowercase
            loggerAPI.debug ('getTicker ' +  t['symbol'] + ':\n ' + str(t))
            return t['markPrice']


def tradeStatus(instrument):
    loggerAPI.info('tradeStatus ' + instrument)
    result = cfPrivate.get_openpositions()
    res = json.loads(result)
    if res['result'] and res['result'] != 'success':
        loggerAPI.warning('tradeStatus Error: ' + res['result'])

    for p in res['openPositions']:
        if p['symbol'] == instrument.lower():
            loggerAPI.info('tradeStatus found: ' + instrument + ' ' + p['side'] + '\n' + str(p))
            maxLev = 0
            if 'maxFixedLeverage' in p:
                maxLev = p['maxFixedLeverage']

            return [p['side'], maxLev, p['size']]

    loggerAPI.warning('tradeStatus: No Postion Found')
    ## no tradeStatus found
    return [None, None, None]

def getAllocation(instrument, PROP, LEV, OPENSIZE):

    [marginEquity, collateralBasic, availableMargin] = getFunds()
    #loggerAPI.info(marginEquity, collateralBasic, availableMargin)
    collateralBasic = 8
    usdCollateral = round(collateralBasic * 0.95 * int(PROP)/100)
    markPrice = getTicker(instrument)

    r = 3

    if markPrice > 1000:
        r = 3
    elif markPrice > 100:
        r = 2
    else:
        r = 1

    assetAmount = usdCollateral/markPrice * int(LEV)
    loggerAPI.warning('FUND CACULATION ' + str(usdCollateral) + ' ' + str(assetAmount))
    try:
        loggerAPI.info('Funds:  Margin ' + str(marginEquity) +  ' ColBasic ' + str(collateralBasic) +  ' availableMargin ' + str(availableMargin))
    except:
        print('logger fail')
    loggerAPI.info('Allocating for ' + instrument + ':\nCollateral $' + str(collateralBasic) +  ':\nCollateral% ' + str(usdCollateral) + '\nAmount of asset on leverage: ' + str(round(assetAmount, r)))

    return round(assetAmount, r)

def getStopPrice(instrument, STOP, SIDE):
    STOPPRICE = 0.0

    markPrice = getTicker(instrument)

    STOPPRICE = markPrice - int(STOP)

    if SIDE == 'sell':
        STOPPRICE = markPrice + int(STOP)

        ## get mark price
    loggerAPI.info('getStopPrice: ' + str(STOPPRICE))
    return STOPPRICE

def closeOpen(instrument, STOP, PROP, LEV, STOPCANCEL, TSsize, TS):
    loggerAPI.info('closeOpen init data: ' + instrument + ' ' + TS + ' ' + str(TSsize))
    try:
        CLOSESIZE = TSsize

        SIDE = None
        CLOSESIDE = None
        STOPSIDE = None

        if TS == 'long':
            SIDE = 'sell'
            STOPSIDE = 'buy'
            CLOSESIDE = 'sell'
        elif TS == 'short':
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
        loggerAPI.info(closeResult)
        if len(closeRes['sendStatus']) < 2:
            #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
            loggerAPI.warning('closeOrder Error: ' + str(closeRes['sendStatus']))
            return {'error': closeResult, 'instrument': instrument}
        loggerAPI.info('CLOSE POSITION:\n' + closeResult)

        ### Close last stop order
        result = cfPrivate.cancel_order(STOPCANCEL)
        loggerAPI.info("cancel_order:\n" + str(result))

        SIZE = getAllocation(instrument, PROP, LEV, TSsize) # size not really necessary as new prop and lev would mean new size calculated

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
            loggerAPI.warning('openOrder Error: ' + str(openRes['sendStatus']))
            return {'error': openResult, 'instrument': instrument}
        loggerAPI.info('OPEN POSITION:\n' + openResult)

        OPENID = openRes['sendStatus']['order_id']

        STOPPRICE = getStopPrice(instrument, STOP, SIDE)
        CLIENTID = instrument + '_' + str(STOPPRICE)

        stopOrder = {
            "orderType": "stp",
            "symbol": instrument,
            "side": STOPSIDE,
            "size": SIZE,
            "stopPrice" : STOPPRICE,
            "triggerSignal": "mark_price",
            "cliOrdId": CLIENTID,
            "reduceOnly": "true",
            "triggerSignal" : "mark"
        }

        stopResult = cfPrivate.send_order_1(stopOrder)
        stopRes = json.loads(stopResult)
        if len(stopRes['sendStatus']) < 2:
            #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
            loggerAPI.warning('stopOrder Error: ' + str(stopRes['sendStatus']))
            return {'error': stopResult, 'instrument': instrument}
        loggerAPI.info('STOP POSITION:\n' + stopResult)

        STOPID = stopRes['sendStatus']['order_id']
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        return {'TIME': date_time, 'status': 'CLOSE/OPEN ', 'side': SIDE, 'instrument': instrument, 'STOPID': STOPID, 'OPENID': OPENID }
    except Exception as e:
        loggerAPI.warning('CLOSE OPEN EXCEPTION:  ' + str(e))



def openPosition(instrument, STOP, PROP, LEV, SIDE):
    loggerAPI.info('Open init data: ' + instrument + ' ' + SIDE + ' ' + str(PROP) + '% ' + str(LEV) + 'x')
    try:
        SIZE = getAllocation(instrument, PROP, LEV, None)

        STOPSIDE = 'sell'

        if SIDE == 'sell':
            STOPSIDE = 'buy'


        openOrder = {
            "orderType": "mkt",
            "symbol": instrument.lower(),
            "side": SIDE,
            "size": SIZE
        }
        print('OPEN ORDER', instrument, openOrder)
        openResult = cfPrivate.send_order_1(openOrder)


        openRes = json.loads(openResult)
        print('OPEN RES 1', openRes)
        if len(openRes['sendStatus']) < 2:
            #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
            loggerAPI.info('openNewOrder Error: ' + str(openRes['sendStatus']))
            return {'error': openResult, 'instrument': instrument}
        loggerAPI.info('OPEN NEW POSITION:\n' + openResult)

        OPENID = openRes['sendStatus']['order_id']

        STOPPRICE = getStopPrice(instrument, STOP, SIDE)
        CLIENTID = instrument + '_' + str(STOPPRICE)
        stopOrder = {
            "orderType": "stp",
            "symbol": instrument,
            "side": STOPSIDE,
            "size": SIZE,
            "stopPrice" : STOPPRICE,
            "cliOrdId": CLIENTID,
            "reduceOnly": "true",
            "triggerSignal" : "mark"
        }

        stopResult = cfPrivate.send_order_1(stopOrder)
        stopRes = json.loads(stopResult)
        print('STOP RES 1', openRes)
        if len(stopRes['sendStatus']) < 2:
            #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
            loggerAPI.warning('stopNewOrder Error: ' + str(stopRes['sendStatus']))
            return {'error': stopResult, 'instrument': instrument}
        loggerAPI.info('STOP NEW POSITION:\n' + stopResult)

        STOPID = stopRes['sendStatus']['order_id']
        loggerAPI.info('STOP NEW ORDER ' + STOPID)

        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        return {'TIME': date_time, 'status': 'START NEW POSITION', 'side': SIDE, 'instrument': instrument, 'STOPID': STOPID, 'OPENID': OPENID }

    except Exception as e:
        loggerAPI.warning('OPEN POSITION EXCEPTION:  ' + str(e))

