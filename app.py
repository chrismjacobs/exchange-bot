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

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    errorList = errors[instrument]
    errorList.insert(0, msg + '//' + date_time)

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
        addAlert(ticker, 'Asset not found on Kraken futures')
        return False

    return instrument

@app.route("/webhook", methods=['POST'])
def tradingview_webhook():

    data = None

    try:
        data = json.loads(request.data)
    except Exception as e:
        print('DATA LOAD EXCEPTION')
        addAlert('tradingview', str(e))
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

    print(assets.keys())

    if instrument not in assets:
        assets[instrument] = {
            'lev' : 2,
            'prop' : 0,
            'stop' : 0,
            'webhooks' : [data],
            'trades' : [],
            'laststop' : 0,
            'lastprop' : 0,
        }
        errors[instrument] = []
        r.set('assets', json.dumps(assets))
        r.set('errors', json.dumps(errors))
        return 'Done'
    elif assets[instrument]['prop'] == 0:
        addAlert(instrument, ': No allocation proportion set ' +  ' ' + json.dumps(assets[instrument]))
        return 'Done'

    assets[instrument]['webhooks'].insert(0, data)
    STOP = assets[instrument]['stop']
    PROP = assets[instrument]['prop']
    LEV = assets[instrument]['lev']
    STOPID = assets[instrument]['laststop']
    tradeResult = tradeAsset(instrument, SIDE, STOP, PROP, LEV, STOPID)
    print('TRADE RESULT ', tradeResult)
    try:
        if tradeResult != False:
            assets[instrument]['webhooks'].insert(0, data)
            assets[instrument]['trades'].insert(0, tradeResult)
            assets[instrument]['laststop'] = tradeResult['STOPID']
            assets[instrument]['lastprop'] = PROP
            r.set('assets', json.dumps(assets))
    except Exception as e:
        print('EXCEPTION ON TRADE RESULT ', e)




    return 'TRADING VIEW WEBHOOK'


def tradeAsset(instrument, SIDE, STOP, PROP, LEV, STOPID):

    TSlist = tradeStatus(instrument)
    TS = TSlist[0]
    if TS == 'long' and SIDE == 'buy':
        print('NO ACTION ' + instrument)
        return False

    elif TS == 'short' and SIDE == 'sell':
        print('NO ACTION ' + instrument)
        return False

    elif TS == 'long' and SIDE == 'sell':
        tradeData = closeOpen(instrument, STOP, PROP, LEV, STOPID)
        if 'error' in tradeData:
            addAlert(instrument, tradeData)
            return False
        return tradeData

    elif TS == 'short' and SIDE == 'buy':
        tradeData = closeOpen(instrument, STOP, PROP, LEV, STOPID)
        if 'error' in tradeData:
            addAlert(instrument, tradeData)
            return False
        return tradeData

    elif TS == None:
        tradeData = openPosition(instrument, STOP, PROP, LEV, SIDE)
        print('New Postion ', tradeData)
        if 'error' in tradeData:
            addAlert(instrument, tradeData)
            return False
        return tradeData

    else:
        addAlert(instrument, 'tradeStatus: ' + TS)
        return False


@app.route('/getFunds', methods=['POST'])
def getFunds():
    pw = request.form ['pw']
    if int(pw) != int(CODE):
        return {'error' : 'authentication'}


    # if pw != PASSWORD:
    #     return abort
    return json.dumps(getFunds())


@app.route('/getAssets', methods=['POST'])
def getAssets():
    pw = request.form ['pw']
    if int(pw) != int(CODE):
        return {'error' : 'authentication'}

    assets = json.loads(r.get('assets'))
    errors = json.loads(r.get('errors'))

    for a in assets:
        assets[a]['price'] = getTicker(a)
        TSlist = tradeStatus(a)
        print(TSlist)
        assets[a]['position'] = TSlist[0]
        assets[a]['lastlev'] = TSlist[1]
        assets[a]['errors'] = errors[a]

    return json.dumps(assets)



@app.route('/setAsset', methods=['POST'])
def setAsset():
    pw = request.form ['pw']
    if int(pw) != int(CODE):
        return {'error' : 'authentication error'}

    # pw = request.form ['pw']
    asset = request.form['asset']
    stop = request.form['stop']
    lev = request.form['lev']
    prop = request.form['prop']

    assets = json.loads(r.get('assets'))
    assets[asset]['stop'] = float(stop)
    assets[asset]['lev'] = float(lev)
    assets[asset]['prop'] = float(prop)

    r.set('assets', json.dumps(assets))

    return {'success' : 'assets updated'}








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)