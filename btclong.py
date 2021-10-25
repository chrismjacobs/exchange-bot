import bybit
import config
import time

'''##### edit trade info #####'''

sideBS = 'Buy'
top = 56866 #first entry
bottom = 56306 # last entry
stop = None
profit = None
ladder = 'normal'  ### see spread options below
entries = 20 # number of entries if ladder = 'normal' otherwise spread list  length will be used
fraction = 0.8 # The proportion of availble fund to use on the trade
leverage = 3
'''IMPORTANT! must be the same as set on account'''

spread = {
    'normal' : [], # This setting will use an even spread of entries
    # can add custom spread, one fraction for each entry, totol must = 1
    'increase': [0.072, 0.078, 0.084, 0.090, 0.097, 0.103, 0.110, 0.116, 0.122, 0.128],
    'weighted': [0.070, 0.074, 0.080, 0.090, 0.095, 0.105, 0.110, 0.120, 0.128, 0.130],
    'decrease': [0.128, 0.122, 0.116, 0.110, 0.103,  0.097, 0.090, 0.084, 0.078, 0.072],
    'bell': [0.081, 0.091, 0.098, 0.109, 0.121, 0.121, 0.109, 0.098, 0.091, 0.081]
    }

#################################################################

client = bybit.bybit(test=False, api_key=config.api_key, api_secret=config.api_secret)
print(client)
btcFunds = client.Wallet.Wallet_getBalance(coin="BTC").result()[0]['result']['BTC']['available_balance']
print(btcFunds)

# print BTC price
print(client.Market.Market_symbolInfo().result()[0]['result'][0]['last_price'])


if ladder != 'normal':
    entries = len(spread[ladder])

difference = top - bottom
increment = difference/(entries-1)
count = 0  # DO NOT CHANGE COUNT

for i in range(entries):
    price = round(top - increment * i)
    if ladder == 'normal':
        dollars = round((btcFunds * price * fraction * leverage)/entries)
    else:
        dollars = round(  (btcFunds * price * fraction * leverage) * spread[ladder][count]  )
        count += 1
    print(client.Order.Order_new(side=sideBS,symbol="BTCUSD",order_type="Limit",stop_loss=stop,take_profit=profit,qty=dollars,price=price,time_in_force="GoodTillCancel").result())
    print(price, dollars)


