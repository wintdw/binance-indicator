from binance.client import Client
from binance.enums import *
import json
import yaml

class BinanceOpts():
  def __init__(self):
    api_key = ""
    secret_key = ""
    with open("/etc/binance/telegram.yaml") as f:
      y = yaml.safe_load(f)
      api_key = y["APIKEY"]
      secret_key = y["SECRETKEY"]
    self.client = Client(api_key, secret_key)
    self.client.ping()

  #### ORDER
  def create_marketbuy_order(self, symbol, quantity):
    order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
    print((json.dumps(order, indent=4)))

  def create_limitbuy_order(self, symbol, quantity, price):
    order = self.client.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
    print((json.dumps(order, indent=4)))

  def create_marketsell_order(self, symbol, quantity):
    order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
    print((json.dumps(order, indent=4)))
    
  def create_limitsell_order(self, symbol, quantity, price):
    order = self.client.order_limit_sell(symbol=symbol, quantity=quantity, price=price)
    print((json.dumps(order, indent=4)))
  ###########

  def check_symbol_price(self, symbol):
    info = self.client.get_all_tickers()
    for price in info:
      if price["symbol"] == symbol:
        return float(price["price"])
  
  def check_asset_balance(self, asset):
    info = self.client.get_asset_balance(asset=asset)
    return float(info["free"])

#### Thread functions
def worker_balance(binance, infodict, coin):
  infodict[coin] = binance.check_asset_balance(coin)

def worker_symbolprice(binance, infodict, symbol):
  infodict[symbol] =  binance.check_symbol_price(symbol)

def worker_klines(binance, infodict, symbol, timeperiod):
  if "d" in timeperiod:
    timelength = int(timeperiod.replace("d", "")) * 150 * 24
  elif "h" in timeperiod:
    timelength = int(timeperiod.replace("h", "")) * 150
  else:
    timelength = int(int(timeperiod.replace("m", "")) * 150 / 60)
  infodict["klines"+timeperiod] = binance.client.get_historical_klines(symbol, timeperiod, "{} hours ago UTC".format(timelength))
