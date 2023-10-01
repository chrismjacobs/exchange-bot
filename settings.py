import json
import os
from functools import wraps
import redis
from flask import make_response, request

LOCAL = False

try:
    import config as config
    SECRET_KEY = config.SECRET_KEY
    REDIS_URL = config.REDIS_URL
    API_KEY_KRAKEN = config.API_KEY_KRAKEN
    API_SEC_KRAKEN = config.API_SEC_KRAKEN
    DEMO_API_KEY_KRAKEN = config.DEMO_API_KEY_KRAKEN
    DEMO_API_SEC_KRAKEN = config.DEMO_API_SEC_KRAKEN
    EXCHANGE = config.EXCHANGE
    USER = config.USER
    PASSWORD = config.PASSWORD
    CODE = config.CODE
    LOCAL = True
    DEBUG = True
    print('CONFIG SUCCESS')
except:
    print('ACCESS OS ENVIRON CREDENTIALS')
    SECRET_KEY = os.environ['SECRET_KEY']
    API_KEY_KRAKEN = os.environ['API_KEY_KRAKEN']
    API_SEC_KRAKEN = os.environ['API_SEC_KRAKEN']
    DEMO_API_KEY_KRAKEN = os.environ['DEMO_API_KEY_KRAKEN']
    DEMO_API_SEC_KRAKEN = os.environ['DEMO_API_SEC_KRAKEN']
    USER = os.environ['USER']
    CODE = int(os.environ['CODE'])
    PASSWORD = os.environ['PASSWORD']
    REDIS_URL = os.environ['REDIS_URL']
    EXCHANGE = os.environ['EXCHANGE']
    DEBUG = False


APIPATH = "https://futures.kraken.com"

if EXCHANGE.lower() == 'demo':
    API_KEY_KRAKEN = DEMO_API_KEY_KRAKEN
    API_SEC_KRAKEN = DEMO_API_SEC_KRAKEN
    APIPATH = "https://demo-futures.kraken.com"

if REDIS_URL:
    if LOCAL:
        r = redis.from_url(REDIS_URL, ssl_cert_reqs=None, decode_responses=True)
    else:
        ## For Render URL
        r = redis.from_url(REDIS_URL, decode_responses=True)

        ## For Heroku Redis
        # r = redis.Redis(
        #     host = 'redis-12011.c54.ap-northeast-1-2.ec2.cloud.redislabs.com',
        #     port = 12011,
        #     password = REDIS_PASSWORD,
        #     decode_responses = True # get python friendly format
        # )

    print('REDIS', r)
    print('REDIS', r.keys())

    lastVersion = r.get('version')
    if not lastVersion:
        r.set('version', EXCHANGE.lower())
    elif lastVersion != EXCHANGE.lower():
        r.delete('assets')
        r.delete('errors')
        r.set('version', EXCHANGE.lower())

    if not r.get('assets'):
        r.set('assets', json.dumps({}))
    if not r.get('errors'):
        r.set('errors', json.dumps({}))

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        username = USER
        passcode = PASSWORD

        if auth and auth.username == username and auth.password == passcode:
            return f(*args, **kwargs)
        return make_response("<h1>Access denied!</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    return decorated

