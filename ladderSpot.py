import bybit
from config import keys
from datetime import datetime, timedelta
#from checklist import volume


'''##### edit trade info #####'''


'''
account = 1
coin = 'ETH'
top = 2180 # first entry
bottom = 2164# last entry
stop = 2140
profit = 4050
leverage = 2
'''

# sideBS = "Buy"
# account = 2
# coin = 'BTC'
# top = 58500 # first entry
# bottom = 57500 #last entry
# stop = 57000
# profit = 64000

sideBS = "Buy"
account = 1
coin = 'BTC'
top = 39518 # first entry
bottom =  39480 #last entry
stop = 39466
'''if BTC is weak you can't have stop and you shouldn't put on the trade'''
profit = 39722



# top = 41980 # first entry
# bottom =  41269 #last entry
# stop = 40775

# top = 46511 # first entry
# bottom =  46687 #last entry
# stop = 46938

leverage = 3
'''IMPORTANT! must be the same as set on account'''

action = 15

ladder = 'increase2'  ### see spread options below
entries = 20 # number of entries if ladder = 'normal' otherwise spread list length will be used
fraction = 0.4 # The proportion of availble fund to use on the trade


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
    'bell': [0.071, 0.091, 0.098, 0.109, 0.131, 0.131, 0.109, 0.098, 0.091, 0.071]
    }

#################################################################

print(keys[account])
client = bybit.bybit(test=False, api_key=keys[account]['api_key'], api_secret=keys[account]['api_secret'])
print(client)

funds = client.Wallet.Wallet_getBalance(coin=coin).result()[0]['result'][coin]['available_balance']
print(funds)

# print BTC price
last_price = client.Market.Market_symbolInfo().result()[0]['result'][0]['last_price']


if ladder != 'normal':
    entries = len(spread[ladder])

difference = top - bottom
increment = difference/(entries-1)
count = 0  # DO NOT CHANGE COUNT


pair = coin + 'USD'

if action > 1:
    for i in range(entries):
        price = round(top - increment * i)
        if ladder == 'normal':
            dollars = round((funds * price * fraction * leverage)/entries)
            count += 1
        else:
            dollars = round(  (funds * price * fraction * leverage) * spread[ladder][count]  )
            count += 1
        result = client.Order.Order_new(side=sideBS,symbol=pair,order_type="Limit",stop_loss=stop,take_profit=profit,qty=dollars,price=price,time_in_force="GoodTillCancel").result()

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
print(round(funds*fraction,3))
print(round(funds*fraction*lev_loss, 3))
print(round(fraction*lev_loss, 3))
print('% RISK', round(fraction*lev_loss, 3))
print('% PROFIT', round(fraction*lev_profit, 3))
print(sideBS)
if action > 0:
    print('DONE')
else:
    print('NO ACTION')





