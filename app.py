from flask import Flask, request, render_template, jsonify, abort
import json
import time
import datetime
from settings import SECRET_KEY, r, CODE, auth_required
from exchangeAPI import apiFunds, apiTicker, apiOrder


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True


@app.route('/')
@auth_required
def home():

    context = {}

    return render_template('trading.html', **context)


@app.route('/getFunds', methods=['POST'])
def getFunds():
    # pw = request.form ['pw']
    tickerFunds = request.form ['tickerFunds']

    # if pw != PASSWORD:
    #     return abort
    return apiFunds(tickerFunds)


@app.route('/getOrder', methods=['POST'])
def getOrder():
    print(request.form)
    ORDERTYPE = request.form['mode']
    PRICE = request.form['price']
    STOP = request.form['stop']
    PROFIT = request.form['profit']
    SIDE = request.form['side'].lower()
    VOLUME = request.form['volume']
    print(ORDERTYPE, SIDE, VOLUME, PRICE, STOP, PROFIT)

    LEV = 0

    order = apiOrder(ORDERTYPE, SIDE, VOLUME, PRICE, LEV)

    #r.lpush('trades', json.dumps(order))
    if len(order['error']) == 0 and ORDERTYPE == 'limit':
        revSide = 'buy'
        if SIDE == revSide:
            revSide = 'sell'
        print('SETTING STOP')
        apiOrder('stop-loss', revSide, VOLUME, STOP, LEV)
        # print('SETTING TP')
        # apiOrder('take-profit', 'buy', VOLUME, PROFIT, LEV)

    # if pw != PASSWORD:
    #     return abort
    return order


@app.route('/getTicker', methods=['POST'])
def getTicker():
    # pw = request.form ['pw']
    ticker = request.form ['ticker']

    # if pw != PASSWORD:
    #     return abort
    return apiTicker(ticker)

@app.route('/getAlerts', methods=['POST'])
def getAlerts():
    print('getAerts')

    alerts = r.lrange('alerts', 0, -1)

    # if pw != PASSWORD:
    #     return abort
    return json.dumps(alerts)

@app.route('/getTrades', methods=['POST'])
def getTrades():

    trades = r.lrange('trades', 0, -1)

    return json.dumps(trades)


@app.route("/webhook", methods=['POST'])
def tradingview_webhook():

    print(request)
    data = json.loads(request.data)
    print('TV DATA', data)

    r.lpush('alerts', json.dumps(data))

    return 'TRADING VIEW'


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