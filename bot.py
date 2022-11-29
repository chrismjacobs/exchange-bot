from flask import Flask, request, render_template, jsonify, abort
import meta
import json
import time
import base64
import datetime
from meta import session, s3_resource
from pybit import usdt_perpetual, inverse_perpetual
from app import app

@app.route("/tradingview-to-webhook-order", methods=['POST'])
def tradingview_webhook():
    data = json.loads(request.data)
