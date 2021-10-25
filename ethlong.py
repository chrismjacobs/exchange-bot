import bybit
import config
import time

'''##### edit trade info #####'''

sideBS = 'Buy'
top = 1740# first entry
bottom = 1720 # last entry
stop = 1710
profit = 2000
ladder = 'normal'  ### see spread options below
entries = 20 # number of entries if ladder = 'normal' otherwise spread list length will be used (see below, usually 10)
fraction = 0.8  # The proportion of availble fund to use on the trade
leverage = 3  # IMPORTANT! must be the same as set on account

spread = {
    'normal' : [], # This setting will use an even spread of entries
    # can add custom spread, one fraction for each entry, total must = 1, entries must equal 10
    'increase': [0.072, 0.078, 0.084, 0.090, 0.097, 0.103, 0.110, 0.116, 0.122, 0.128],
    'decrease': [0.128, 0.122, 0.116, 0.110, 0.103,  0.097, 0.090, 0.084, 0.078, 0.072],
    'bell': [0.081, 0.091, 0.098, 0.109, 0.121, 0.121, 0.109, 0.098, 0.091, 0.081]
    }

#################################################################

client = bybit.bybit(test=False, api_key=config.api_key, api_secret=config.api_secret)
ethFunds = client.Wallet.Wallet_getBalance(coin="ETH").result()[0]['result']['ETH']['available_balance']
print(ethFunds)

# print ETH price
print(client.Market.Market_symbolInfo().result()[0]['result'][1]['last_price'])


if ladder != 'normal':
    entries = len(spread[ladder])

difference = top - bottom
increment = difference/(entries-1)
count = 0  # DO NOT CHANGE COUNT

for i in range(entries):
    price = round(top - increment * i)
    if ladder == 'normal':
        dollars = round((ethFunds * price * fraction * leverage)/entries, 2) # round 2 to give decomal place on dollars
    else:
        dollars = round((ethFunds * price * fraction * leverage) * spread[ladder][count], 2)
        count += 1
    print(client.Order.Order_new(side=sideBS,symbol="ETHUSD",order_type="Limit",stop_loss=stop,take_profit=profit,qty=dollars,price=price,time_in_force="GoodTillCancel").result())
    print(price, dollars)



# cancel all orders
#print(client.Order.Order_cancelAll(symbol="BTCUSD").result())