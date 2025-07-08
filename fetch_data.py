import requests
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timedelta

api_key = "1B1AV8OI48Q0KOGJ"



def fetch_option_chain(ticker):
    stock = yf.Ticker(ticker)
    # Choose an expiration date (pick the first one for example)
    expiration_dates = stock.options
    expiration = expiration_dates[0]  # e.g., '2024-07-12'
    nearest_expiration = expiration_dates[0]
    # Fetch the option chain for that expiration
    option_chain = stock.option_chain(expiration)
    # Separate calls and puts
    calls = option_chain.calls
    puts = option_chain.puts
    result = pd.merge(calls, puts, on='strike', suffixes=('_call', '_put'))

    return result, nearest_expiration


def fetch_stock_data(ticker,start,end):
    historical_prices = yf.download(ticker,start, end)
    historical_prices['logreturn'] = np.log(historical_prices['Close'] / historical_prices['Close'].shift(1))
    historical_prices = historical_prices.dropna()
    return historical_prices


#this function constructs the volatility cone and returns a dataframe including the min,max and the percentiles
def volatilityCone(stock_data):
  window_sizes = [2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  volatility_stats = {
      'window': [],
      'min_volatility': [],
      'max_volatility': [],
      '25th_percentile': [],
      'median_volatility': [],
      '75th_percentile': []
  }

  for window in window_sizes:
      rolling_volatility = stock_data['logreturn'].rolling(window=window).std()
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

#this functions plots the volatility cone
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
today = datetime.today()
start = today - timedelta(200)  # this is the date i download the historical stock price to construct the vol cone
end = today - timedelta(1)



stock_data = fetch_stock_data(ticker,start,end)
VC=volatilityCone(stock_data)


optionchain,nearest_expiry= fetch_option_chain(ticker)
nearest_expiry = datetime.strptime(nearest_expiry, '%Y-%m-%d')
diff = nearest_expiry - today  # timedelta object
num_days = diff.days

ticker_today = stock_data['Close'].iloc[-1]
optionchain = optionchain[(optionchain['strike'] < ticker_today.values[0] + 3) & (optionchain['strike'] > ticker_today.values[0] - 3)]
optionchain['averageIV'] = (optionchain['impliedVolatility_call'] + optionchain['impliedVolatility_put']) / 2


# Step 1: Get the 25th percentile for the selected window
threshold = VC[VC["window"] == num_days]["75th_percentile"].values[0]
# Step 2: produce signal
trade_signal = optionchain[optionchain['averageIV'] < threshold]
print(VC)
print(trade_signal)


LONG1 = None
LONG2 = None

if not trade_signal.empty:
    # Select the row with the lowest averageIV
    best_row = trade_signal.loc[trade_signal['averageIV'].idxmin()]

    LONG1 = best_row['contractSymbol_call']
    LONG2 = best_row['contractSymbol_put']

    print("\nBest signal found (lowest averageIV):")
    print(f"LONG1: {LONG1}")
    print(f"LONG2: {LONG2}")
    print(f"averageIV: {best_row['averageIV']:.6f}")
    print("------")
else:
    print("\nWith the provided conditions, no signals found.")
