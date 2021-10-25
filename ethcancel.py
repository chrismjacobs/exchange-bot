import bybit
import config
import time

print(config.api_key)

client = bybit.bybit(test=False, api_key=config.api_key, api_secret=config.api_secret)

# cancel all orders
print(client.Order.Order_cancelAll(symbol="ETHUSD").result())