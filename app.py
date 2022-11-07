from flask import Flask, request, render_template, jsonify, abort
import meta
import json
import time
import base64
import boto3
import datetime
from meta import session, s3_resource
from pybit import usdt_perpetual, inverse_perpetual

session_unauth_USD = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)
session_unauth_USDT = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

print(session_unauth_USD.open_interest(
    symbol="BTCUSD",
    period="5min"
))

currentDate = datetime.date.today()
month = currentDate.strftime("%B")

print(currentDate)
print(month)


app = Flask(__name__)
app.config['SECRET_KEY'] = meta.SECRET_KEY
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def home(pw):


    return 'trading desk'

@app.route('/trade/<string:pw>')
def trade(pw):
    if pw != meta.PASSWORD:
        return abort

    print ('get MetaFile')
    bucket = 'rekt-journal'
    key = 'tradeJournal_' + month + '.json'

    # with open('static/' + key, 'r') as json_file:
    #     file_content = json_file

    content_object = s3_resource.Object( bucket, key )
    file_content = content_object.get()['Body'].read().decode('utf-8')


    return render_template('tradingdesk.html', tradeJournal=file_content)

@app.route('/journal/<string:pw>')
def journal(pw):
    if pw != meta.PASSWORD:
        return abort

    mList = [
        'October',
        'November'
    ]

    bucket = 'rekt-journal'

    jDict = {

    }

    for m in mList:

        key = 'tradeJournal_' + m + '.json'
        content_object = s3_resource.Object( bucket, key )
        file_content = content_object.get()['Body'].read().decode('utf-8')

        jDict[m] = json.loads(file_content)


    return render_template('journaldesk.html', tradeJournal=json.dumps(jDict))


@app.route('/getData', methods=['POST'])
def getData():
    pw = request.form ['pw']

    if pw != meta.PASSWORD:
        return abort

    mode = request.form ['mode']
    side = request.form ['side']
    minutes = request.form ['minutes']
    risk = float(request.form ['risk'])
    first = float(request.form ['first'])
    fraction = float(request.form ['fraction'])
    stop = float(request.form ['stop'])
    leverage = float(request.form ['leverage'])


    print('SIDE: ', side, minutes, risk, fraction, stop, first)

    latest = session_unauth_USD.latest_information_for_symbol(symbol="BTCUSD")
    latest2 = session_unauth_USDT.latest_information_for_symbol(symbol="BTCUSDT")
    getBTC = latest['result'][0]
    getBTC2 = latest2['result'][0]
    print('latest', latest)
    print('open interest', getBTC['open_interest'], getBTC2['open_interest'], round(float(latest['time_now'])))

    oi1 = session.open_interest(symbol="BTCUSD", period="5min", limit=6)['result']
    oi2 = session.open_interest(symbol="BTCUSDT", period="5min", limit=6)['result']
    ls = session.long_short_ratio(symbol="BTCUSD", limit=1, period="5min")['result']
    print('OI1\n', oi1, '\nOI2\n', oi2, ls)

    oiDict1 = {
        1 : getBTC['open_interest'],
        2 : oi1[0]['open_interest'],
        3 : oi1[1]['open_interest'],
        4 : oi1[2]['open_interest']
    }

    oiDict2 = {
        1 : getBTC2['open_interest'],
        2 : oi2[0]['open_interest'],
        3 : oi2[1]['open_interest'],
        4 : oi2[2]['open_interest']
    }

    if mode == 'first':
        price = float(getBTC['last_price'])
        return jsonify({'result' : price, 'mode' : mode })
    if mode == 'oiData':
        return jsonify({'mode' : mode, 'oi1' : json.dumps(oiDict1), 'oi2' : json.dumps(oiDict2), 'ls': json.dumps(ls[0])})
    elif mode == 'leverage':

        position = session.my_position(symbol="BTCUSD")['result']
        print(position)
        positionSize = position['size']
        positionLev = float(position['leverage'])


        print('LEV: ', side, risk, fraction, positionSize, positionLev, leverage)

        if positionSize == 0 and positionLev != leverage:
            leverage = setLeverage(first, stop, risk, fraction, leverage)
        else:
            mode = 'alert'
            leverage = 'leverage no change'

        return jsonify({'result' : leverage, 'mode' : mode})

    elif mode == 'stop':
        price = getHiLow(minutes, side)

        stopAdjust = {
            'Buy' : price - 10,
            'Sell' : price + 10
        }

        stop = stopAdjust[side]

        return jsonify({'result' : stop, 'mode' : mode})

    elif mode == 'funds':
        print('getFunds', session.announcement())
        funds = session.get_wallet_balance()['result']['BTC']['equity']
        return jsonify({'result' : funds, 'mode' : mode})


@app.route('/getTrade', methods=['POST'])
def getTrade():
    pw = request.form ['pw']

    if pw != meta.PASSWORD:
        return abort

    mode = request.form ['mode']
    spread = int(request.form ['spread'])
    price = int(request.form ['price'])
    fraction = float(request.form ['fraction'])

    position = session.my_position(symbol="BTCUSD")['result']
    print('position', position)
    latest = session.latest_information_for_symbol(symbol="BTCUSD")['result'][0]
    print('latest', latest)

    positionSide = position['side']
    positionSize = int(position['size'])


    if mode == 'size':
        result = positionSize
        mode = 'action'

    elif mode == 'cancel':
        result = session.cancel_all_active_orders(symbol="BTCUSD")['ret_msg']
        mode = 'action'

    elif mode == 'price':
        result =  str(round(float(latest['last_price'])))

    elif mode == 'limit':

        if price == 0:
            currentPrice = round(float(latest['last_price']))

            limitPrice = {
                'Buy' : currentPrice + spread,
                'Sell' : currentPrice - spread
            }

            price = limitPrice[positionSide]

        options = ['Sell', 'Buy']
        options.remove(positionSide)
        side = options[0]
        stop = None
        value = price

        print(side, value, stop, positionSize, fraction)

        result = placeOrder(side, value, stop, positionSize*fraction)



    return jsonify({'result' : result, 'mode' : mode})

@app.route('/getOrder', methods=['POST'])
def getOrder():
    pw = request.form ['pw']

    if pw != meta.PASSWORD:
        return abort

    mode = request.form ['mode']
    side = request.form ['side']
    first = float(request.form ['first'])
    spread = float(request.form ['spread'])
    ladder = int(request.form ['ladder'])
    fraction = float(request.form ['fraction'])
    stop = float(request.form ['stop'])
    leverage = float(request.form ['leverage'])

    spreadArray = []

    position = session.my_position(symbol="BTCUSD")['result']
    price = float(session.latest_information_for_symbol(symbol="BTCUSD")['result'][0]['last_price'])
    funds = session.get_wallet_balance()['result']['BTC']['equity']

    ### check/set leverage
    positionLev = float(position['leverage'])
    if float(leverage) != positionLev:
        session.set_leverage(symbol="BTCUSD", leverage=leverage)

    if first == None or first == 0:
        first = price

    start = 1
    if ladder == 1:
        start = 0
    for i in range(start, ladder+1):
        if side == 'Buy':
            spreadArray.append(first - i*spread)
        else:
            spreadArray.append(first + i*spread)

    qty = (price * funds * leverage) * fraction
    print('QTY', price, funds, leverage, qty)

    result = None

    for value in spreadArray:
        result = placeOrder(side, value, stop, qty/len(spreadArray))

    return jsonify({'result' : result})


@app.route('/recordTrade', methods=['POST'])
def recordTrade():
    pw = request.form ['pw']

    if pw != meta.PASSWORD:
        return abort

    record = request.form ['record']
    imageArray = request.form ['imageArray']
    currentTrade = request.form ['currentTrade']

    print ('put MetaFile')
    bucket = 'rekt-journal'
    key = 'tradeJournal_' + month + '.json'

    # with open('static/' + key, 'r') as json_file:
    #     file_content = json_file
    # print(key, json_file, type(file_content))
    # jload = json.loads(file_content)

    content_object = s3_resource.Object( bucket, key )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)


    jload[currentTrade] = {}
    jload[currentTrade]['record'] = json.loads(record)
    jload[currentTrade]['imageArray'] = json.loads(imageArray)

    with open('static/' + key, 'w') as json_file:
        json.dump(jload, json_file)

    jstring = json.dumps(jload)
    s3_resource.Bucket(bucket).put_object(
        Key=key, Body=jstring)

    print('json put in bucket location', bucket, key)

    return jsonify({'result' : 'trade recorded'})

@app.route('/addImage', methods=['POST'])
def addImage():
    pw = request.form ['pw']

    if pw != meta.PASSWORD:
        return abort

    b64data = request.form ['b64data']
    imageArray = request.form ['imageArray']
    currentTrade = request.form ['currentTrade']

    print(imageArray, type(imageArray))
    imageSet = json.loads(imageArray)

    count = len(imageSet) + 1

    S3_LOCATION = 'https://rekt-journal.s3.ap-northeast-1.amazonaws.com/'
    S3_BUCKET_NAME = 'rekt-journal'
    print('PROCESSING IMAGE')
    image = base64.b64decode(b64data)
    filename = month + '/' + str(currentTrade) + '/' + str(count) +'.png'
    imageLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)

    imageSet[count] = imageLink

    return jsonify({'result' : json.dumps(imageSet)})



def setLeverage(first, stop, risk, fraction, leverage):

    if first == None or first == 0:
        first = float(session.latest_information_for_symbol(symbol="BTCUSD")['result'][0]['last_price'])

    distance = abs(first - stop)

    percent_difference = (distance/first)*100  # as decimal

    lev = round((risk/percent_difference)*fraction, 1)

    print(first, stop, distance, percent_difference, lev)

    if risk == 0:
        lev = leverage

    if lev < 1:
        print('Leverage too low', lev)
    else:
        print(session.set_leverage(symbol="BTCUSD", leverage=lev))

    return lev

def getHiLow(minutes, side):

    from datetime import datetime
    now = datetime.now()
    timestamp = int(datetime.timestamp(now)) - int(minutes)*60

    data = session.query_kline(symbol="BTCUSD", interval="1", from_time=str(timestamp))['result']

    print('GET HI LOW ', len(data))


    hAry = []
    lAry = []

    for i in range(0, len(data)):

        hAry.append(int(data[i]['high'].split('.')[0]))
        lAry.append(int(data[i]['low'].split('.')[0]))

    mHi = max(hAry)
    mLow = min(lAry)

    print(mLow)

    if side == 'Buy':
        return mLow
    else:
        return mHi

def placeOrder(side, price, stop_loss, qty):

    order = session.place_active_order(
    symbol="BTCUSD",
    side=side,
    order_type='Limit',
    price=price,
    stop_loss = stop_loss,
    take_profit = None,
    qty=qty,
    time_in_force="GoodTillCancel"
    )


    message = order['ret_msg']
    data = json.dumps(order['result'])

    print('ORDER', order)
    print('MESSAGE', message)
    print('DATA', data)

    return data

def shareImage(b64data, log, count, month):

    S3_LOCATION = 'https://rekt-journal-lms.s3.ap-northeast-1.amazonaws.com/'
    S3_BUCKET_NAME = 'rekt-journal'
    print('PROCESSING IMAGE')
    image = base64.b64decode(b64data)
    filename = month + '/' + str(log) + '/' + str(count) +'.png'
    imageLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)
    return imageLink

def putJson(data, log, month):
    print ('put MetaFile')


    key = 'tradeJournal_' + month + '.json'
    string = "static/" + key

    with open(string, "r") as f:
        jload = json.load(f)

    jload[log] = json.load(data)

    bucket = 'rekt-journal'
    jstring = json.dumps(jload)
    s3_resource.Bucket(bucket).put_object(
        Key=key, Body=jstring)

    print('json put in bucket location', bucket, key)

    return 'ok'

if __name__ == '__main__':
    app.run()