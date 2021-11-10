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

  # Threading
  thrds = []
  thrds.append(threading.Thread(target=indicator.worker_symbolprice, args=(dwb, infodict, ticker,)))
  thrds.append(threading.Thread(target=indicator.worker_klines, args=(dwb, infodict, ticker, timep,)))
  for t in thrds:
    t.start()
  for t in thrds:
    t.join()

  ind = indicator.calculate_indicator(infodict, timep)
  data = indicator.gather_data(infodict, timep)
  pd = graph.draw(data, ind, ticker, timep)

  noti.notify(ticker, timep, ind, data, pd, threshold=20)
