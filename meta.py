import boto3
import json
import os
from pybit import inverse_perpetual, usdt_perpetual
import redis

try:
    import config
    API_KEY = config.API_KEY
    API_SECRET = config.API_SECRET
    AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
    SECRET_KEY = config.SECRET_KEY
    PASSWORD = config.PASSWORD
    REDIS_URL = config.REDIS_URL
    REDIS_PASSWORD = config.REDIS_PASSWORD
    print('SUCCESS')
except:
    print('EXCEPTION')
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    API_KEY = os.environ['API_KEY']
    API_SECRET= os.environ['API_SECRET']
    PASSWORD= os.environ['PASSWORD']



session = inverse_perpetual.HTTP(
    endpoint='https://api.bybit.com',
    api_key= API_KEY,
    api_secret=API_SECRET
)

print('bybit session', session)


s3_resource = boto3.resource('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

print('S3', s3_resource)

session_unauth_USD = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)
session_unauth_USDT = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

# print(session_unauth_USD.open_interest(
#     symbol="BTCUSD",
#     period="5min"
# ))


if REDIS_URL:
    # r = redis.from_url(REDIS_URL)
    r = redis.Redis(
        host = 'redis-12011.c54.ap-northeast-1-2.ec2.cloud.redislabs.com',
        port = 12011,
        password = REDIS_PASSWORD,
        decode_responses = True # get python freiendlt format
    )

    print('REDIS', r)