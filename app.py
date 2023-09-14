from flask import Flask, request, render_template, jsonify, abort
import json
import time
import datetime
from meta import SECRET_KEY, PASSWORD, r
from exchangeAPI import apiFunds, apiTicker


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True


@app.route('/')
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


@app.route('/getTicker', methods=['POST'])
def getTicker():
    # pw = request.form ['pw']
    ticker = request.form ['ticker']

    # if pw != PASSWORD:
    #     return abort
    return apiTicker(ticker)


@app.route("/webhook", methods=['POST'])
def tradingview_webhook():
    data = json.loads(request.data)
    print('TV DATA', data)
    r.set('LAST ALERT', json.dumps(data))


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