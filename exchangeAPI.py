import json
import time
import datetime
import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import requests

from settings import API_KEY_KRAKEN, API_SEC_KRAKEN, r


api_url = "https://api.kraken.com"
api_key = API_KEY_KRAKEN
api_sec = API_SEC_KRAKEN

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Read Kraken API key and secret stored in environment variables

# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def apiFunds(tickerFunds):
    # Construct the request and print the result


    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_sec)


    print(tickerFunds, resp.json())

    if tickerFunds != '':
        return resp.json()
    else:
        return resp.json()



def apiTicker(TICKER):

    resp = requests.get('https://api.kraken.com/0/public/Ticker?pair=' + TICKER)
    print(resp.json())
    return resp.json()

def apiOrder(ORDERTYPE, SIDE, VOLUME, PRICE, LEV):

    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "ordertype": ORDERTYPE,
        "type": SIDE,
        "volume": VOLUME,
        "pair": "BTCUSD",
        "price": PRICE,
        #"leverage": 2

    }, api_key, api_sec)

    print(resp.json())

    return resp.json()

def apiCancelAll():
    resp = kraken_request('/0/private/CancelOrder', {
        "nonce": str(int(1000*time.time())),
        "txid": "OU3QQB-7G2XE-QOZOS5"
    }, api_key, api_sec)