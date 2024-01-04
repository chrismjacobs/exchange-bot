import json
import os
from functools import wraps
from flask import make_response, request

LOCAL = False

try:
    import config as config
    SECRET_KEY = config.SECRET_KEY
    API_KEY = config.API_KEY
    API_SECRET = config.API_SECRET
    USER = config.USER
    PASSWORD = config.PASSWORD
    CODE = config.CODE
    LOCAL = True
    DEBUG = True
    print('CONFIG SUCCESS')
except:
    print('ACCESS OS ENVIRON CREDENTIALS')
    SECRET_KEY = os.environ['SECRET_KEY']
    USER = os.environ['USER']
    PASSWORD = os.environ['PASSWORD']
    API_KEY = os.environ['API_KEY']
    API_SECRET = os.environ['API_SECRET']
    CODE = os.environ['CODE']
    DEBUG = False


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

