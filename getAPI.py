import os
import json
import krakenAPI as kAPI
import datetime


# API_KEY_KRAKEN = os.getenv('API_KEY_KRAKEN')
# API_SEC_KRAKEN = os.getenv('API_SEC_KRAKEN')
# EXCHANGE = os.getenv('EXCHANGE')
try:
    import config

    REDIS_URL = config.REDIS_URL
    API_KEY_KRAKEN = config.API_KEY_KRAKEN
    API_SEC_KRAKEN = config.API_SEC_KRAKEN
    EXCHANGE = config.EXCHANGE
    print('CONFIG SUCCESS')
except:
    print('ACCESS OS ENVIRON CREDENTIALS')
    API_KEY_KRAKEN = os.environ['API_KEY_KRAKEN']
    API_SEC_KRAKEN = os.environ['API_SEC_KRAKEN']
    REDIS_URL = os.environ['REDIS_URL']
    EXCHANGE = os.environ['EXCHANGE']

print(API_KEY_KRAKEN)
print(API_SEC_KRAKEN)
print(EXCHANGE)

# accessible on your Account page under Settings -> API Keys
apiPublicKey = API_KEY_KRAKEN
# accessible on your Account page under Settings -> API Keys
apiPrivateKey = API_SEC_KRAKEN

apiPath = "https://futures.kraken.com"

if EXCHANGE == 'DEMO':
    apiPath = "https://demo-futures.kraken.com"

timeout = 20
checkCertificate = True  # when using the test environment, this must be set to "False"
useNonce = False  # nonce is optional


cfPublic = kAPI.cfApiMethods(apiPath,
                             timeout=timeout,
                             checkCertificate=checkCertificate
                             )
cfPrivate = kAPI.cfApiMethods(apiPath,
                              timeout=timeout,
                              apiPublicKey=apiPublicKey,
                              apiPrivateKey=apiPrivateKey,
                              checkCertificate=checkCertificate,
                              useNonce=useNonce
                              )


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

def closeOpen(instrument, STOP, PROP, LEV):
    result = cfPrivate.get_openpositions()
    res = json.loads(result)
    for p in res['openPositions']:
        if p['symbol'] == instrument:
            print('tradeStatus found:\n ' + instrument + ' ' + p['side'] + '\n' + str(p))
            SIZE = p['size']
            SIDE = 'buy'
            CLOSE = 'sell'
            if p['side'] == 'short':
                CLOSE = 'buy'
                SIDE = 'sell'

            closeOrder = {
                "orderType": "mkt",
                "symbol": instrument,
                "side": CLOSE,
                "size": SIZE
            }
            closeResult = cfPrivate.send_order_1(closeOrder)
            closeRes = json.loads(closeResult)
            if closeRes['result'] and closeRes['result'] != 'success':
                #{'result': 'success', 'sendStatus': {'status': 'invalidSize'}, 'serverTime': '2023-09-19T07:01:43.680Z'}
                print('closeOrder Error: ' + closeRes['result'])
            print(closeRes)

            openOrder = {
                "orderType": "mkt",
                "symbol": instrument,
                "side": SIDE,
                "size": SIZE
            }
            openResult = cfPrivate.send_order_1(openOrder)
            openRes = json.loads(openResult)
            if openRes['result'] and openRes['result'] != 'success':
                print('openOrder Error: ' + openRes['result'])
            print(openRes)

def openPosition(instrument, STOP, PROP, LEV):

            SIDE = 'buy'

            openOrder = {
                "orderType": "mkt",
                "symbol": instrument,
                "side": SIDE,
                "size": 0.5
            }
            openResult = cfPrivate.send_order_1(openOrder)
            openRes = json.loads(openResult)
            if openRes['result'] and openRes['result'] != 'success':
                print('openNewOrder Error: ' + openRes['result'])
            print(openRes)



def getFunds():
    result = cfPrivate.get_accounts()
    res = json.loads(result)
    if res['result'] and res['result'] != 'success':
        print('getFunds Error: ' + res['result'])

    print("get_accounts:\n", res['accounts'].keys())
    # dict_keys(['result', 'accounts', 'serverTime'])

    print(res['accounts']['flex'])
    marginEquity = res['accounts']['flex']['marginEquity']
    collateralBasic = res['accounts']['flex']['marginEquity'] - res['accounts']['flex']['totalUnrealized']
    availableMargin = res['accounts']['flex']['availableMargin']
    return (marginEquity, collateralBasic, availableMargin)


instrument = 'pf_xbtusd'

closeOpen(instrument, 0,0,0)

#tradeStatus(instrument, 5)
