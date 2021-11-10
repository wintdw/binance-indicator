import plotly.graph_objects as go
import plotly.figure_factory
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy.signal import find_peaks

# get from gather_data & calculate_value
def draw(data, ind, ticker, timep):
  price = go.Candlestick(x=data["time"], open=data["open"], high=data["high"], low=data["low"], close=data["close"], name="Price")
  vol = go.Bar(x=data["time"], y=data["vol"], name="Volume")
  rsi = go.Scatter(x=data["time"], y=ind["rsi"], name="RSI", fillcolor="aliceblue")
  mfi = go.Scatter(x=data["time"], y=ind["mfi"], name="MFI", fillcolor="olive")
  ema = go.Scatter(x=data["time"], y=ind["ema"], name="EMA_100")
  #highbb = go.Scatter(x=data["time"], y=ind["BB"][0], showlegend=False, line=go.scatter.Line(color="#FFBAD2"))
  #lowbb = go.Scatter(x=data["time"], y=ind["BB"][2], showlegend=False, line=go.scatter.Line(color="#FFBAD2"))
  #ema = go.Scatter(x=data["time"], y=ind["BB"][1], line=go.scatter.Line(color="yellow"))

  # Peaks/Dips work best for BTC only
  peaks = find_peaks(data["close"], prominence=100, distance=10)[0][-2:]
  dips = find_peaks([-x for x in data["close"]], prominence=100, distance=10)[0][-2:]

  #peak_price = go.Scatter(x=[data["time"][j] for j in peaks], y=[data["close"][j] for j in peaks], showlegend=False, mode='markers', marker=dict(size=8, color='purple', symbol='cross'))
  peak_price_line = go.Scatter(x=[data["time"][j] for j in peaks], y=[data["close"][j] for j in peaks], showlegend=False, marker=dict(size=8, color='purple', symbol='cross'))
  peak_rsi_line = go.Scatter(x=[data["time"][j] for j in peaks], y=[ind["rsi"][j] for j in peaks], showlegend=False, marker=dict(size=8, color='purple', symbol='cross'))
  peak_mfi_line = go.Scatter(x=[data["time"][j] for j in peaks], y=[ind["mfi"][j] for j in peaks], showlegend=False, marker=dict(size=8, color='burlywood', symbol='cross'))
  #dip_price_line = go.Scatter(x=[data["time"][j] for j in dips], y=[data["close"][j] for j in dips], showlegend=False, marker=dict(size=8, color='purple', symbol='cross'))
  #dip_rsi_line = go.Scatter(x=[data["time"][j] for j in dips], y=[ind["rsi"][j] for j in dips], showlegend=False, marker=dict(size=8, color='purple', symbol='cross'))

  fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3])
  fig.update_yaxes(side="right") 
  for t in [price, peak_price_line, ema]:
    fig.add_trace(t, row=1, col=1)
  #for t in [vol, ema_vol]:
  #  fig.add_trace(t, row=2, col=1)
  for t in [rsi, mfi, peak_rsi_line, peak_mfi_line]:
    fig.add_trace(t, row=2, col=1)

  fig.update_layout(xaxis_rangeslider_visible=False, width=1920, height=1080)

  pio.write_image(fig,'/var/itim/{}_{}.png'.format(ticker, timep))

  return {"peaks": peaks,"dips": dips}
#####
