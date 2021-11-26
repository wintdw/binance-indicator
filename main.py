import datetime
import threading
import binanceopts
import alert
import indicator
import sys
import graph

if __name__ == "__main__":
  dwb = binanceopts.BinanceOpts()
  noti = alert.Alert()
  infodict = {}
  ticker = sys.argv[1]
  timep = sys.argv[2]
  
  # for peakdips
  prominence = None
  if ticker == "BTCUSDT":
    prominence = 100


  # Threading
  thrds = []
  thrds.append(threading.Thread(target=binanceopts.worker_symbolprice, args=(dwb, infodict, ticker,)))
  thrds.append(threading.Thread(target=binanceopts.worker_klines, args=(dwb, infodict, ticker, timep,)))
  for t in thrds:
    t.start()
  for t in thrds:
    t.join()

  data = indicator.gather_data(infodict, timep)
  ind = indicator.calculate_indicator(data)
  pd = indicator.find_peakdips(data, prominence)

  # Drap graphs
  graph.draw(data, ind, pd, ticker, timep)

  noti.notify(ticker, timep, ind, data, pd, threshold=80)
