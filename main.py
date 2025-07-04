import numpy as np
from scipy.stats import norm
#api_key = "1B1AV8OI48Q0KOGJ"

class Options:

    def __init__(self,S, K, T, r, sigma):
        self.S = S                  # underlying price
        self.K = K                  # strike price
        self.T = T                  # time to maturity
        self.r = r                  # risk-free rate
        self.sigma = sigma          # volatility

    def BS_call(self):
        d1 = (np.log(self.S/self.K) + (self.r + self.sigma**2/2)*self.T) / (self.sigma*np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        call_price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return call_price

    def BS_put(self):
        d1 = (np.log(self.S / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return put_price

