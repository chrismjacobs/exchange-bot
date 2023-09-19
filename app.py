from flask import Flask, request, render_template, jsonify, abort
import json
import time
import datetime
from settings import SECRET_KEY, r, CODE, auth_required
# from exchangeAPI import apiFunds, apiTicker, apiOrder
from getAPI import getInstruments, tradeStatus, closeOpen, openPosition


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True


@app.route('/')
@auth_required
def home():

    context = {}

    return render_template('trading.html', **context)

def addAlert(msg):
    r.lpush('alerts', msg)


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

    data = json.loads(request.data)
    print('TV DATA', data)
    print('TV DATA', type(data))
    print('TV DATA', data.keys())
    if not data['TVCODE']:
        addAlert('No TVCODE found in webhook alert')
        return False
    elif data['TVCODE'] != CODE:
        addAlert('TVCODE in webhook alert is incorrect')
        return False
    else:
        print('CODE ERROR')


    TICKER = data['TICKER']
    TIME = data['TIME']
    SIDE = data['SIDE']

    print(TICKER)

    instrument = checkTicker(TICKER)
    if not instrument:
        return False


    assets = json.loads(r.get('assets'))

    if instrument not in assets:
        assets[instrument] = {
            'lev' : 5,
            'prop' : 80,
            'stop' : 200,
            'webhooks' : [json.dumps(data)],
            'trades' : []
        }
        return False
    elif assets[instrument]['prop'] == 0:
        addAlert(instrument + ': No allocation proportion set')
        return False
    elif assets[instrument]['lev'] < 2:
        addAlert(instrument + ': Double check leverage is same as exchange (>2)')
        return False
    elif assets[instrument]['stop'] == 1:
        addAlert(instrument + ': Set appropriate stop')
        return False

    assets[instrument]['webhooks'].append(data)
    STOP = assets[instrument]['stop']
    PROP = assets[instrument]['prop']
    LEV = assets[instrument]['lev']
    tradeResult = tradeAsset(instrument, SIDE, STOP, PROP, LEV)
    if tradeResult:
        assets[instrument]['webhooks'].append(tradeResult)

    r.set('assets', json.dumps(assets))
    return 'TRADING VIEW WEBHOOK'

def tradeAsset(instrument, SIDE, STOP, PROP, LEV):

    TS = tradeStatus(instrument, LEV)
    if TS == 'long' and SIDE == 'buy':
        print('NO ACTION ' + instrument)
        return False

    elif TS == 'long' and SIDE == 'sell':
        tradeData = closeOpen(instrument, STOP, PROP, LEV)
        if tradeData['error']:
            addAlert(tradeData['error'])
            return False
        return tradeData

    elif TS == 'short' and SIDE == 'sell':
        print('NO ACTION ' + instrument)
        return False

    elif TS == 'short' and SIDE == 'buy':
        tradeData = closeOpen(instrument, STOP, PROP, LEV)
        if tradeData['error']:
            addAlert(tradeData['error'])
            return False
        return tradeData

    elif TS == None:
        tradeData = openPosition(instrument, STOP, PROP, LEV, SIDE)
        if tradeData['error']:
            addAlert(tradeData['error'])
            return False
        return tradeData

    else:
        addAlert(TS)




# @app.route('/getFunds', methods=['POST'])
# def getFunds():
#         # pw = request.form ['pw']
#     tickerFunds = request.form ['tickerFunds']

#     # if pw != PASSWORD:
#     #     return abort
#     return apiFunds(tickerFunds)


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


# @app.route('/getTicker', methods=['POST'])
# def getTicker():
#     # pw = request.form ['pw']
#     ticker = request.form ['ticker']

#     # if pw != PASSWORD:
#     #     return abort
#     return False #apiTicker(ticker)

# @app.route('/getAlerts', methods=['POST'])
# def getAlerts():
#     print('getAerts')

#     alerts = r.lrange('alerts', 0, -1)

#     # if pw != PASSWORD:
#     #     return abort
#     return json.dumps(alerts)

# @app.route('/getLutfi', methods=['POST'])
# def getLutfi():
#     print('getLutfi')

#     alerts = r.lrange('lutfi', 0, -1)

#     # if pw != PASSWORD:
#     #     return abort
#     return json.dumps(alerts)

# @app.route('/getTrades', methods=['POST'])
# def getTrades():

#     trades = r.lrange('trades', 0, -1)

#     return json.dumps(trades)




# @app.route("/lutfi", methods=['POST'])
# def tradingview_lutfi():

#     print(request)
#     data = json.loads(request.data)
#     print('TV DATA', data)

#     r.lpush('lufti', json.dumps(data))

#     return 'TRADING VIEW'


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