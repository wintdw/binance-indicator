import telepot
import yaml
import os
from datetime import datetime

class Alert():
  def __init__(self):  
    token = ""
    cred = "/etc/binance/telegram.yaml"
    self.lockfile = "/etc/binance/"
    self.chatid = ""
    with open(cred) as f:
      y = yaml.safe_load(f)
      token = y["TOKEN"]
      self.chatid = y["CHATID"]
    self.bot = telepot.Bot(token)

  # 1% near the top 3 SRs
  # 1: Near SR
  # 0: Not
  def sr(self, data, pd, accuracy=0.001):
    for i in pd["SRs"][:3]:
      if data["close"][-1] <= data["close"][i]*(1+accuracy) and data["close"][-1] >= data["close"][i]*(1-accuracy):
        return (1, data["close"][i])
    return (0, data["close"][pd["SRs"][-1]])

  # 1: Higher than EMA_100
  # 2: Lower than EMA_100
  def ema(self, ind, data):
    if data["close"][-1] > ind["ema"][-1]: 
      return 1
    return 2

  # 0: Normal
  # 1: Overbought
  # 2: Oversold
  def mfi(self, ind, threshold=70):
    if ind["mfi"][-1] >= threshold:
      return 1
    elif ind["mfi"][-1] <= (100-threshold):
      return 2
    else:
      return 0

  # 0: Normal
  # 11: Peak Convergence
  # 12: Peak Divergence
  # 21: Dip Convergence
  # 22: Dip Divergence
  def mfi_div_conv(self, data, pd, ind):
    if data["close"][pd["peaks"][0]] > data["close"][pd["peaks"][1]] and ind["mfi"][pd["peaks"][0]] < ind["mfi"][pd["peaks"][1]]:
      return 11
    elif data["close"][pd["peaks"][0]] < data["close"][pd["peaks"][1]] and ind["mfi"][pd["peaks"][0]] > ind["mfi"][pd["peaks"][1]]:
      return 12
    if data["close"][pd["dips"][0]] > data["close"][pd["dips"][1]] and ind["mfi"][pd["dips"][0]] < ind["mfi"][pd["dips"][1]]:
      return 21
    elif data["close"][pd["dips"][0]] < data["close"][pd["dips"][1]] and ind["mfi"][pd["dips"][0]] > ind["mfi"][pd["dips"][1]]:
      return 22
    else:
      return 0

  # 1: break
  # 0: normal
  def break_peak(self, data, pd):
    latest_peak = data["close"][pd["peaks"][-1]]
    if data["close"][-2] < latest_peak and data["close"][-1] > latest_peak:
      return 1
    return 0

  def sendMsg(self, text, msg_type, symbol, timep):
    lockfile = "{}{}{}_{}".format(self.lockfile, symbol, timep, msg_type)
    if not os.path.exists(lockfile):
      self.bot.sendMessage(self.chatid, text)
      open(lockfile, 'a').close()
      return
    mtime = os.path.getmtime(lockfile)
    now = datetime.now().strftime('%s')
    if (int(now) - int(mtime)) >= 180:   # 3mins delay
      self.bot.sendMessage(self.chatid, text)
      os.utime(lockfile)

  def notify(self, symbol, timep, ind, data, pd, threshold=70):
    send = False
    text = "[{}]\nPrice: {:.2f} [{:.2f} - {:.2f}]\nMFI: {:.2f}".format(symbol, data["close"][-1], ind["ema"][-1], data["close"][pd["SRs"][0]], ind["mfi"][-1])
    image = "/var/itim/{}_{}.png".format(symbol, timep)
    mfi = self.mfi(ind, threshold)
    mfi_divconv = self.mfi_div_conv(data, pd, ind)
    ema = self.ema(ind, data)
    sr_near, sr_price = self.sr(data, pd)
    brk = self.break_peak(data, pd)

    if brk == 1:
      send = True
      msg_type = "break_peak"
      text = text + "\n" + timep + " Peak Break!"

    if mfi == 2:
      send = True
      msg_type = "mfi"
      text = text + "\n" + timep + " Oversold!"
    elif mfi == 1:
      send = True
      msg_type = "mfi"
      text = text + "\n" + timep + " Overbought!"

    #self.bot.sendPhoto(CHAT_ID, photo=open(image, 'rb'), caption=text)
    if mfi_divconv == 22 and ema == 1:
      send = True
      msg_type = "mfi_divconv"
      text = text + "\n" + timep + " Div Conv -> Buy!"
    elif mfi_divconv == 12:
      send = True
      msg_type = "mfi_divconv"
      text = text + "\n" + timep + " Peak Div!"

    if sr_near == 1:
      send = True
      msg_type = "sr"
      text = text + "\n" + timep + " Near SR " + str(sr_price)

    if send:
      self.sendMsg(text, msg_type, symbol, timep)
      #self.bot.sendMessage(self.chatid, text)
    print(text)
