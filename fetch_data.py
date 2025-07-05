import requests
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timedelta

api_key = "1B1AV8OI48Q0KOGJ"
today = datetime.today()
start = today - timedelta(1000)
end = today - timedelta(1)

def fetch_option_chain():
    url = (
    "https://www.alphavantage.co/query?"
    "function=HISTORICAL_OPTIONS"
    "&symbol={ticker}"
    "&date=2025-07-01"
    f"&apikey={api_key}"
    )
    resp = requests.get(url)
    data = resp.json()
    df = pd.DataFrame(data)
    normalized_data = pd.json_normalize(df['data'])
    # Concatenate it back with the rest of df (optional)
    result = pd.concat([df.drop(columns=['data']), normalized_data], axis=1)
    return result


def fetch_stock_data(ticker,start,end):
    historical_prices = yf.download(ticker,start, end)
    historical_prices['logreturn'] = np.log(historical_prices['Close'] / historical_prices['Close'].shift(1))
    return historical_prices

def volatilityCone(ticker,start,end):
  data = fetch_stock_data(ticker,start,end)
  window_sizes = [10,25, 50,75,120]
  volatility_stats = {
      'window': [],
      'min_volatility': [],
      'max_volatility': [],
      '25th_percentile': [],
      'median_volatility': [],
      '75th_percentile': []
  }

  for window in window_sizes:
      rolling_volatility = data['logreturn'].rolling(window=window).std()
      rolling_volatility = rolling_volatility.dropna()
      rolling_volatility = rolling_volatility *np.sqrt(252)
      volatility_stats['window'].append(window)
      volatility_stats['min_volatility'].append(rolling_volatility.min())
      volatility_stats['max_volatility'].append(rolling_volatility.max())
      volatility_stats['25th_percentile'].append(rolling_volatility.quantile(0.25))
      volatility_stats['median_volatility'].append(rolling_volatility.quantile(0.5))
      volatility_stats['75th_percentile'].append(rolling_volatility.quantile(0.75))

  volatility_cone = pd.DataFrame(volatility_stats)
  return volatility_cone

def plotVC(ticker,start,end):
  VC = volatilityCone(ticker,start,end)

  plt.figure(figsize=(10, 6))

  plt.plot(VC["window"], VC["min_volatility"], label="Min Volatility", linestyle="-", color="blue")
  plt.plot(VC["window"], VC["max_volatility"], label="Max Volatility", linestyle="-", color="red")
  plt.plot(VC["window"], VC["25th_percentile"], label="25th Percentile", linestyle="--", color="green")
  plt.plot(VC["window"], VC["median_volatility"], label="Median Volatility", linestyle="--", color="black", linewidth=1.5)
  plt.plot(VC["window"], VC["75th_percentile"], label="75th Percentile", linestyle="--", color="purple")
  plt.xticks(ticks=VC["window"], labels=VC["window"], fontsize=10)
  plt.xlabel("Window Size (Days)", fontsize=12)
  plt.title("Volatility Cone", fontsize=14)
  plt.xlabel("Window Size (Days)", fontsize=12)
  plt.ylabel("Volatility", fontsize=12)
  plt.legend(loc="upper right")
  plt.grid(alpha=0.3)
  plt.show()



ticker ='AAPL'
print(volatilityCone(ticker,start,end))
plotVC(ticker,start,end)