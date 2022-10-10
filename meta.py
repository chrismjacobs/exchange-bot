import boto3
import json
import os
from pybit import inverse_perpetual

try:
    import config
    keys = config.keys
    API_KEY = keys[1]['api_key'],
    API_SECRET = keys[1]['api_secret']
    AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
    SECRET_KEY = config.SECRET_KEY
    print('SUCCESS')
except:
    print('EXCEPT')
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    API_KEY = os.environ['API_KEY'] ,
    API_SECRET= os.environ['API_SECRET']



session = inverse_perpetual.HTTP(
    endpoint='https://api.bybit.com',
    api_key=API_KEY,
    api_secret=API_SECRET
)

print('bybit session', session)

ws = inverse_perpetual.WebSocket(
    test=False,
    api_key=keys[1]['api_key'],
    api_secret=keys[1]['api_secret']
)

s3_resource = boto3.resource('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

print('S3', s3_resource)