from flask import Flask, request, render_template, jsonify, abort
import json
import time
import datetime
from settings import SECRET_KEY, r, CODE, auth_required
# from exchangeAPI import apiFunds, apiTicker, apiOrder
from getAPI import getInstruments, tradeStatus, closeOpen, openPosition, getFunds, getTicker


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True


@app.route('/')
@auth_required
def home():

    context = {}

    return render_template('trading.html', **context)

def addAlert(instrument, msg):



    errors = json.loads(r.get('errors'))

    if instrument not in errors:
        errors[instrument] = []

    errorList = errors[instrument]
    errorList.insert(0, msg)

    r.set('errors', json.dumps(errors))
    return True


def checkTicker(ticker):
    print('CHECK TICKER')
    if 'USD' not in ticker:
        addAlert('USD not found in ticker')
        return False

    asset = ticker.split('USD')[0]
    instrument = getInstruments(asset)
    if instrument == None:
        addAlert('Asset not found on Kraken futures')
        return False

    return instrument

@app.route("/webhook", methods=['POST'])
def tradingview_webhook():

    data = None

    try:
        data = json.loads(request.data)
    except Exception as e:
        print('DATA LOAD EXCEPTION')
        addAlert('tradingview', e)
        return 'ERROR'
    print('TV DATA', data)
    print('TV DATA', type(data))
    print('TV DATA', data.keys())
    try:
        print(data['TVCODE'])
        if not data['TVCODE']:
            addAlert('tradingview', 'No TVCODE found in webhook alert ' + request.data)
            return 'ERROR'
        elif int(data['TVCODE']) != int(CODE):
            addAlert('tradingview', 'TVCODE in webhook alert is incorrect' + request.data)
            return 'ERROR'
        else:
            print('CODE SUCCESS')

    except Exception as e:
        print ('EXCEPTION ', e)



    TICKER = data['TICKER']
    TIME = data['TIME']
    SIDE = data['SIDE']

    print(TICKER)

    instrument = checkTicker(TICKER)
    print('ticker check', instrument)


    assets = json.loads(r.get('assets'))
    errors = json.loads(r.get('errors'))

    print(assets)

    if instrument not in assets:
        assets[instrument] = {
            'lev' : 5,
            'prop' : 80,
            'stop' : 200,
            'webhooks' : [json.dumps(data)],
            'trades' : [],
            'laststop' : 0
        }
        errors[instrument] = []
        r.set('assets', json.dumps(assets))
        r.set('errors', json.dumps(errors))
        return 'Done'
    elif assets[instrument]['prop'] == 0:
        addAlert(instrument, ': No allocation proportion set ' + request.data + ' ' + json.dumps(assets[instrument]))
        return 'Done'
    elif assets[instrument]['lev'] < 2:
        addAlert(instrument, ': Double check leverage is same as exchange (>2) ' + request.data + ' ' + json.dumps(assets[instrument]))
        return 'Done'
    elif assets[instrument]['stop'] == 1:
        addAlert(instrument, ': Set appropriate stop ' + request.data + ' ' + json.dumps(assets[instrument]))
        return 'Done'

    assets[instrument]['webhooks'].insert(0, data)
    STOP = assets[instrument]['stop']
    PROP = assets[instrument]['prop']
    LEV = assets[instrument]['lev']
    STOPID = assets[instrument]['laststop']
    tradeResult = tradeAsset(instrument, SIDE, STOP, PROP, LEV, STOPID)
    if tradeResult:
        assets[instrument]['trades'].insert(0, tradeResult)
        assets[instrument]['laststop'] = tradeResult['STOPID']


    r.set('assets', json.dumps(assets))
    return 'TRADING VIEW WEBHOOK'

def tradeAsset(instrument, SIDE, STOP, PROP, LEV, STOPID):

    TS = tradeStatus(instrument, LEV)
    if TS == 'long' and SIDE == 'buy':
        print('NO ACTION ' + instrument)
        return False

    elif TS == 'short' and SIDE == 'sell':
        print('NO ACTION ' + instrument)
        return False



    elif TS == 'long' and SIDE == 'sell':
        tradeData = closeOpen(instrument, STOP, PROP, LEV, STOPID)
        if 'error' in tradeData:
            addAlert(instrument, json.dumps(tradeData))
            return False
        return tradeData

    elif TS == 'short' and SIDE == 'buy':
        tradeData = closeOpen(instrument, STOP, PROP, LEV. STOPID)
        if 'error' in tradeData:
            addAlert(instrument, json.dumps(tradeData))
            return False
        return tradeData

    elif TS == None:
        tradeData = openPosition(instrument, STOP, PROP, LEV, SIDE)
        if tradeData['error']:
            addAlert(instrument, tradeData['error'])
            return False
        return tradeData

    else:
        addAlert(instrument, 'tradeStatus: ' + TS)


@app.route('/getFunds', methods=['POST'])
def getFunds():
        # pw = request.form ['pw']
    tickerFunds = request.form ['tickerFunds']

    # if pw != PASSWORD:
    #     return abort
    return getFunds()


# @app.route('/getOrder', methods=['POST'])
# def getOrder():
#     print(request.form)
#     ORDERTYPE = request.form['mode']
#     PRICE = request.form['price']
#     STOP = request.form['stop']
#     PROFIT = request.form['profit']
#     SIDE = request.form['side'].lower()
#     VOLUME = request.form['volume']
#     print(ORDERTYPE, SIDE, VOLUME, PRICE, STOP, PROFIT)

#     LEV = 0

#     order = apiOrder(ORDERTYPE, SIDE, VOLUME, PRICE, LEV)

#     #r.lpush('trades', json.dumps(order))
#     if len(order['error']) == 0 and ORDERTYPE == 'limit':
#         revSide = 'buy'
#         if SIDE == revSide:
#             revSide = 'sell'
#         print('SETTING STOP')
#         apiOrder('stop-loss', revSide, VOLUME, STOP, LEV)
#         # print('SETTING TP')
#         # apiOrder('take-profit', 'buy', VOLUME, PROFIT, LEV)

#     # if pw != PASSWORD:
#     #     return abort
#     return order


@app.route('/getTicker', methods=['POST'])
def getTicker():
    # pw = request.form ['pw']
    ticker = request.form ['ticker']

    # if pw != PASSWORD:
    #     return abort
    return getTicker(ticker)

@app.route('/setAsset', methods=['POST'])
def setAsset():

    # pw = request.form ['pw']
    stop = request.form ['stop']
    ticker = request.form ['ticker']
    pw = request.form ['pw']

    markPrice = getTicker(ticker)
    if stop > markPrice / 2:
        return {'alert' : 'stop is greater than 50% of asset'}



    # if pw != PASSWORD:
    #     return abort
    return

# @app.route('/getAlerts', methods=['POST'])
# def getAlerts():
#     print('getAerts')

#     alerts = r.lrange('alerts', 0, -1)

#     # if pw != PASSWORD:
#     #     return abort
#     return json.dumps(alerts)



# @app.route('/getTrade', methods=['POST'])
# def getTrade():
#     pw = request.form ['pw']

#     if pw != PASSWORD:
#         return abort

#     mode = request.form ['mode']
#     spread = int(request.form ['spread'])
#     price = int(request.form ['price'])
#     fraction = float(request.form ['fraction'])
#     profit = None


#     return jsonify({'result' : result, 'mode' : mode})

# @app.route('/getOrder', methods=['POST'])
# def getOrder():
#     pw = request.form ['pw']

#     if pw != PASSWORD:
#         return abort

#     mode = request.form ['mode']
#     side = request.form ['side']
#     first = float(request.form ['first'])
#     spread = float(request.form ['spread'])
#     ladder = int(request.form ['ladder'])
#     fraction = float(request.form ['fraction'])
#     profit = float(request.form ['profit'])
#     stop = float(request.form ['stop'])
#     leverage = float(request.form ['leverage'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)