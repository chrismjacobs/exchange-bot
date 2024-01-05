from flask import Flask, request, render_template, jsonify, abort
import json
import time
import requests
from datetime import datetime
from settings import SECRET_KEY, CODE, DEBUG, auth_required, TG_TOKEN, TG_CHAT
# from exchangeAPI import apiFunds, apiTicker, apiOrder
from openTrade import placeOrder

import logging
# from logger.handlers import SysLogHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG


##logging.basicConfig(level=logging.warning, filename="log.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.warning('Test Logger App')

@app.route('/')
@auth_required
def home():

    context = {}

    return render_template('trading.html', **context)

def addAlert(instrument, msg):
    errors = json.loads(r.get('errors'))

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")


    if instrument not in errors:
        errors['misc'].insert(0, msg + '//' + date_time)
        instrument = 'misc'

    errorList = errors[instrument]
    errorList.insert(0, msg + '//' + date_time)


    r.set('errors', json.dumps(errors))
    return True


# def checkTicker(ticker):
#     logger.warning('CHECK TICKER ' + ticker)
#     if 'USD' not in ticker:
#         addAlert(ticker, 'USD not found in ticker')
#         return False

#     asset = ticker.split('USD')[0]
#     instrument = getInstruments(asset)
#     if instrument == None:
#         addAlert(ticker, 'Asset not found on Kraken futures')
#         return False

#     return instrument.upper()

def sendMessage(m):
    url_string = 'https://api.telegram.org/bot' + TG_TOKEN + '/sendMessage?chat_id=' + str(TG_CHAT)
    base_url = url_string + '&text="{}"'.format(m)
    print(base_url)
    requests.get(base_url)

@app.route("/webhook", methods=['POST'])
def tradingview_webhook():

    data = None

    try:
        data = json.loads(request.data)
    except Exception as e:
        logger.warning('DATA LOAD EXCEPTION ' + str(e))
        addAlert('tradingview', 'Invalid json data')
        return 'ERROR'
    logger.warning('TV DATA' +  json.dumps(data))

    try:
        ##logger.warning(data['TVCODE'])
        if not data['code']:
            addAlert('tradingview', 'No TVCODE found in webhook alert')
            return 'ERROR'
        elif int(data['code']) != int(CODE):
            addAlert('tradingview', 'TVCODE in webhook alert is incorrect')
            return 'ERROR'
        else:
            logger.warning('CODE SUCCESS')

    except Exception as e:
        logger.warning('TV CODE EXCEPTION ' + str(e))

    _sym = data['asset']
    _side = data['side']
    _type = data['type']
    _entry = float(data['entry'])
    _stop = float(data['stop'])
    _profit = float(data['profit'])
    _amt = int(data['amt'])
    _risk = int(data['risk'])

    try:
        resp = placeOrder(_sym,_type, _side, _entry, _amt, _stop, _profit, _risk)
        m = 'TRADE RESULT 1 ' + resp
        logger.warning(m)
        sendMessage(m)
    except Exception as e:
        m = 'TRADE RESULT ERROR 1 ' + str(e)
        logger.warning(m)
        sendMessage(m)

    return 'TV WEBHOOK COMPLETE'


# @app.route('/getData', methods=['POST'])
# def getData():
#     pw = request.form ['pw']
#     if int(pw) != int(CODE):
#         return {'error' : 'authentication code input required'}

#     errors = json.loads(r.get('errors'))

#     if 'misc' not in errors:
#         errors['misc'] = []
#         r.set('errors', json.dumps(errors))

#     dataOBJ = {
#         'funds' : getFunds(),
#         'misc' : errors['misc'],
#         'exchange' : EXCHANGE
#     }


#     # if pw != PASSWORD:
#     #     return abort
#     return json.dumps(dataOBJ)


# @app.route('/getAssets', methods=['POST'])
# def getAssets():
#     pw = request.form ['pw']
#     # if int(pw) != int(CODE):
#     #     return {'error' : 'authentication code'}


#     assets = json.loads(r.get('assets'))
#     errors = json.loads(r.get('errors'))

#     for a in assets:
#         assets[a]['price'] = getTicker(a)
#         TSlist = tradeStatus(a)
#         logger.warning('TSList ' + str(TSlist))
#         assets[a]['position'] = TSlist[0]
#         assets[a]['lastlev'] = TSlist[1]
#         assets[a]['lastsize'] = TSlist[2]
#         assets[a]['errors'] = errors[a]

#     return json.dumps(assets)


# @app.route('/setAsset', methods=['POST'])
# def setAsset():
#     pw = request.form ['pw']
#     if int(pw) != int(CODE):
#         return {'error' : 'authentication error'}

#     asset = request.form['asset']
#     stop = request.form['stop']
#     lev = request.form['lev']
#     prop = request.form['prop']

#     assets = json.loads(r.get('assets'))
#     assets[asset]['stop'] = float(stop)
#     assets[asset]['lev'] = float(lev)
#     assets[asset]['prop'] = float(prop)

#     r.set('assets', json.dumps(assets))

#     return {'success' : 'assets updated'}

# @app.route('/deleteAsset', methods=['POST'])
# def deleteAsset():
#     pw = request.form ['pw']
#     if int(pw) != int(CODE):
#         return {'error' : 'authentication error'}

#     asset = request.form['asset']

#     assets = json.loads(r.get('assets'))

#     removedAsset = assets.pop(asset, asset +' not found')

#     msg = "Removed Asset: " + asset
#     logger.warning(msg)

#     r.set('assets', json.dumps(assets))

#     return {'success' : msg}

# @app.route('/deleteMisc', methods=['POST'])
# def deleteMisc():
#     pw = request.form ['pw']
#     if int(pw) != int(CODE):
#         return {'error' : 'authentication error'}



#     errors = json.loads(r.get('errors'))
#     errors['misc'] = []

#     msg = "Removed Misc Errors"
#     logger.warning(msg)

#     r.set('errors', json.dumps(errors))

#     return {'success' : msg}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)