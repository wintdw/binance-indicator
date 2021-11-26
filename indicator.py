import talib
import numpy
import datetime
import scipy.signal

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

# Input: data from gather_data
def calculate_indicator(data):
  indicators = {}
  highBB, midBB, lowBB = talib.BBANDS(numpy.array(data["close"]), timeperiod=14, matype=talib.MA_Type.EMA)
  indicators["ema"] = talib.EMA(numpy.array(data["close"]), timeperiod=100).tolist()
  indicators["rsi"] = talib.RSI(numpy.array(data["close"]), timeperiod=14).tolist()
  indicators["mfi"] = talib.MFI(numpy.array(data["high"]), numpy.array(data["low"]), numpy.array(data["close"]), numpy.array(data["vol"]), timeperiod=14).tolist()
  indicators["macd"] = talib.MACD(numpy.array(data["close"]), fastperiod=12, slowperiod=26, signalperiod=9)
  indicators["bb"] = (data["close"][-1] - lowBB[-1]) / (highBB[-1] - lowBB[-1])
  indicators["BB"] = [highBB, midBB, lowBB]
  return indicators

# accu = 0.1%
# BTCUSDT prominence=100
def find_peakdips(data, prominence=None, accuracy=0.001):
  peaks_i = scipy.signal.find_peaks(data["close"], prominence=prominence, distance=10)[0].tolist()
  dips_i = scipy.signal.find_peaks([-x for x in data["close"]], prominence=prominence, distance=10)[0].tolist()

  ### Find SRs according to peaks dips
  #pd_i = [data["close"][p] for p in peaks_i] + [data["close"][d] for d in dips_i]
  
  cross_counts = {}
  for i in (peaks_i + dips_i):
    cross_counts[i] = 0
  for i in range(0, len(data["time"])):
    for j in (peaks_i + dips_i):
      if data["high"][i] >= data["close"][j] and data["low"][i] <= data["close"][j]:
        cross_counts[j] += 1
      elif data["high"][i] >= data["close"][j]*(1+accuracy) and data["low"][i] <= data["close"][j]*(1+accuracy):
        cross_counts[j] += 1
      elif data["high"][i] >= data["close"][j]*(1-accuracy) and data["low"][i] <= data["close"][j]*(1-accuracy):
        cross_counts[j] += 1
  ssSR_counts = dict(sorted(cross_counts.items(), key=lambda item: item[1]))
  ssSRs_i = list(ssSR_counts.keys())[::-1]   # Reverse

  # Remove adjacent elements
  def refine_SRs(merge=accuracy):
    deletes = []
    #print(ssSRs_i)
    for i in range(0, len(ssSRs_i)):
      for j in range(i+1, len(ssSRs_i)):
        #print("{} {} {} {}".format(i, j, data["close"][i], data["close"][ssSRs_i[i]]))
        if data["close"][ssSRs_i[i]]*(1+merge) >= data["close"][ssSRs_i[j]] and data["close"][ssSRs_i[i]]*(1-merge) <= data["close"][ssSRs_i[j]]:
          deletes.append(ssSRs_i[j])
          #print("Remove: {}".format(ssSRs_i[j]))
    merge_SRs = [x for x in ssSRs_i if x not in deletes]
    #print(merge_SRs)
    return merge_SRs

  merge_SRs = refine_SRs()

  #print(ssSR_counts)
  #print(merge_SRs)
  #return {"peaks": peaks_i, "dips": dips_i, "SRs": ssSRs_i}
  return {"peaks": peaks_i, "dips": dips_i, "SRs": merge_SRs}
