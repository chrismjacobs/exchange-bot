import bybit
from config import keys, coinlist
from datetime import datetime, timedelta
from checklist import volume

print(keys[1])
client = bybit.bybit(test=False, api_key=keys[1]['api_key'], api_secret=keys[1]['api_secret'])
print(client)

funds = client.Wallet.Wallet_getBalance(coin='USDT').result()[0]['result']['USDT']['available_balance']
print(funds)


'''##### edit trade info #####'''


sideBS = "Buy"


top = 32389 # first entry
bottom = 32100 #last entry
stop = 32000
profit = 32700

leverage = 2
'''IMPORTANT! must be the same as set on account'''

action = 12


ladder = 'normal'  ### see spread options below
entries = 20 # number of entries if ladder = 'normal' otherwise spread list length will be used
fraction = 0.5  # The proportion of availble fund to use on the trade


average = bottom + (top - bottom)/2

basic_loss = 0
lev_loss = 0
lev_profit = 0

if stop:
    basic_loss = round((average - stop)/average, 3)
    lev_loss = round(((average - stop)/average)*leverage, 3)

if profit:
    lev_profit = round(((profit - average)/average)*leverage, 3)


spread = {
    'normal' : [], # This setting will use an even spread of entries
    # can add custom spread, one fraction for each entry, totol must = 1
    'increase': [0.072, 0.078, 0.084, 0.090, 0.097, 0.103, 0.110, 0.116, 0.122, 0.128],
    'increase2': [0.03, 0.039, 0.04, 0.041, 0.042, 0.043, 0.044, 0.045, 0.046, 0.047, 0.048, 0.049, 0.05, 0.051, 0.052, 0.053, 0.054, 0.055, 0.056, 0.057, 0.058],
    'decrease': [0.128, 0.122, 0.116, 0.110, 0.103,  0.097, 0.090, 0.084, 0.078, 0.072],
    'bell': [0.081, 0.091, 0.098, 0.109, 0.121, 0.121, 0.109, 0.098, 0.091, 0.081]
    }

#################################################################

#BTCUSDT = 4
coin_number = 4

# print coin last price
last_price = client.Market.Market_symbolInfo().result()[0]['result'][coin_number]['last_price']

print(coinlist[coin_number], last_price)



''' calculate entry levels '''

if ladder != 'normal':
    entries = len(spread[ladder])

difference = top - bottom
increment = difference/(entries-1)
count = 0  # DO NOT CHANGE COUNT


pair = coinlist[coin_number]
print(pair)

if action > 1:
    for i in range(entries):
        price = round(top - increment * i)
        if ladder == 'normal':
            dollars = round((funds * price * fraction * leverage)/entries)
            count += 1
        else:
            dollars = round(  (funds * price * fraction * leverage) * spread[ladder][count]  )
            count += 1
        result = client.LinearOrder.LinearOrder_new(side=sideBS,symbol=pair,order_type="Limit",stop_loss=stop,take_profit=profit,qty=dollars,price=price,time_in_force="GoodTillCancel").result()
        if count == 1:
            print(result)

        print(price, dollars)


print(datetime.now())
print(last_price)
print(top)
print(bottom)
print(average)
print(ladder)
print(leverage)
print(stop)
print(basic_loss)
print(lev_loss)
print(round(funds, 4))
print(fraction)
print(round(funds*fraction, 3))
print(round(funds*fraction*lev_loss, 3))
print(round(fraction*lev_loss, 3))
print('% RISK', round(fraction*lev_loss, 3))
print('% PROFIT', round(fraction*lev_profit, 3))
if action > 0:
    print('DONE')
else:
    print('NO ACTION')





