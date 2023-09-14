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

from meta import API_KEY_KRAKEN, API_SEC_KRAKEN


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
