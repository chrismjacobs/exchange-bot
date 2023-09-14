import boto3
import json
import os

import redis

LOCAL = False

try:
    import config
    API_KEY = config.API_KEY
    API_SECRET = config.API_SECRET
    AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
    SECRET_KEY = config.SECRET_KEY
    PASSWORD = config.PASSWORD
    REDIS_URL = config.REDIS_URL
    API_KEY_KRAKEN = config.API_KEY_KRAKEN
    API_SEC_KRAKEN = config.API_SEC_KRAKEN
    LOCAL = True
    print('SUCCESS')
except:
    print('EXCEPTION')
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    API_KEY = os.environ['API_KEY']
    API_SECRET= os.environ['API_SECRET']
    PASSWORD= os.environ['PASSWORD']
    REDIS_URL= os.environ['REDIS_URL']



if REDIS_URL:
    if LOCAL:
        r = redis.from_url(REDIS_URL, ssl_cert_reqs=None, decode_responses=True)
    else:
        r = redis.from_url(REDIS_URL)
    # r = redis.Redis(
    #     host = 'redis-12011.c54.ap-northeast-1-2.ec2.cloud.redislabs.com',
    #     port = 12011,
    #     password = REDIS_PASSWORD,
    #     decode_responses = True # get python friendly format
    # )

    print('REDIS', r)
    print('REDIS', r.keys())
    r.set('TEST', 'TEST')
    print('REDIS', r.get('TEST'))