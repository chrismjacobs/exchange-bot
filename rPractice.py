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


from settings import r

r.lpop('alerts')
print(r.lrange('alerts', 0, -1))

