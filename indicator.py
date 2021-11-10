import talib
import numpy
import datetime

#### Thread functions
def worker_balance(binance, infodict, coin):
  infodict[coin] = binance.check_asset_balance(coin)

def worker_symbolprice(binance, infodict, symbol):
  infodict[symbol] =  binance.check_symbol_price(symbol)

def worker_klines(binance, infodict, symbol, timeperiod):
  timelength = "7"
  if timeperiod in ["15m", "5m", "3m", "1m"]:
    timelength = "2"
  infodict["klines"+timeperiod] = binance.client.get_historical_klines(symbol, timeperiod, "{} day ago UTC".format(timelength))

def gather_data(infodict, timeperiod):
  data = {}
  open_data, high_data, low_data, close_data, vol, time_lst = ([] for i in range(6))
  for kline in infodict["klines"+timeperiod]:
    open_data.append(float(kline[1]))
    high_data.append(float(kline[2]))
    low_data.append(float(kline[3]))
    close_data.append(float(kline[4]))
    vol.append(float(kline[5]))
    time_lst.append(datetime.datetime.utcfromtimestamp(int(kline[0])/1000+25200)) #GMT+7
  data["open"] = open_data
  data["high"] = high_data
  data["low"] = low_data
  data["close"] = close_data
  data["vol"] = vol
  data["time"] = time_lst
  return data

def calculate_indicator(infodict, timeperiod):
  data = gather_data(infodict, timeperiod)
  indicators = {}
  highBB, midBB, lowBB = talib.BBANDS(numpy.array(data["close"]), timeperiod=14, matype=talib.MA_Type.EMA)
  indicators["ema"] = talib.EMA(numpy.array(data["close"]), timeperiod=100).tolist()
  indicators["rsi"] = talib.RSI(numpy.array(data["close"]), timeperiod=14).tolist()
  indicators["mfi"] = talib.MFI(numpy.array(data["high"]), numpy.array(data["low"]), numpy.array(data["close"]), numpy.array(data["vol"]), timeperiod=14).tolist()
  indicators["macd"] = talib.MACD(numpy.array(data["close"]), fastperiod=12, slowperiod=26, signalperiod=9)
  indicators["ema_vol"] = talib.EMA(numpy.array(data["vol"]), timeperiod=14)
  indicators["bb"] = (data["close"][-1] - lowBB[-1]) / (highBB[-1] - lowBB[-1])
  indicators["BB"] = [highBB, midBB, lowBB]
  return indicators
