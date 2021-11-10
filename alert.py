import telepot
import yaml

class Alert():
  def __init__(self):  
    token = ""
    self.chatid = ""
    with open("/etc/binance/telegram.yaml") as f:
      y = yaml.safe_load(f)
      token = y["TOKEN"]
      self.chatid = y["CHATID"]
    self.bot = telepot.Bot(token)

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

  def notify(self, symbol, timep, ind, data, pd, threshold=70):
    send = False
    text = "[{}]\nPrice: {:.2f} [{:.2f}]\nMFI: {:.2f}".format(symbol, data["close"][-1], ind["ema"][-1], ind["mfi"][-1])
    image = "/var/itim/{}_{}.png".format(symbol, timep)
    mfi = self.mfi(ind, threshold)
    mfi_divconv = self.mfi_div_conv(data, pd, ind)
    ema = self.ema(ind, data)

    if mfi == 2 and ema == 1:
      send = True
      text = text + "\n" + timep + " Oversold -> Buy!"
    if mfi == 1 and ema == 2:
      send = True
      text = text + "\n" + timep + " Overbought -> Sell!"
    #self.bot.sendPhoto(CHAT_ID, photo=open(image, 'rb'), caption=text)
    #if mfi_divconv == 11:
    #  send = True
    #  text = text + "\n" + timep + " Peak Conv!"
    if mfi_divconv == 12:
      send = True
      text = text + "\n" + timep + " Peak Div -> Sell!"
    if send:
      self.bot.sendMessage(self.chatid, text)
