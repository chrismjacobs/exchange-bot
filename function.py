import json
import time
import base64
import datetime
from meta import session, s3_resource


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

def placeOrder(side, price, stop_loss, qty, take_profit):

    order = session.place_active_order(
    symbol="BTCUSD",
    side=side,
    order_type='Limit',
    price=price,
    stop_loss = stop_loss,
    take_profit = take_profit,
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