import numpy as np
from scipy.stats import norm


class Options:

    def __init__(self,S, K, T, r, sigma):
        self.S = S                  # underlying price
        self.K = K                  # strike price
        self.T = T                  # time to maturity
        self.r = r                  # risk-free rate
        self.sigma = sigma          # volatility

    def d1(self):
        return (np.log(self.S / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))

    def d2(self):
        return self.d1() - self.sigma * np.sqrt(self.T)

    def BS_call(self):
        d1 = self.d1()
        d2 = self.d2()
        call_price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return call_price

    def BS_put(self):
        d1 = self.d1()
        d2 = self.d2()
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return put_price


class Greeks(Options):
    def __init__(self, S, K, T, r, sigma):
        super().__init__(S, K, T, r, sigma)
    
    def delta_call(self):
        d1 = self.d1()
        return norm.cdf(d1)
    
    def delta_put(self):
        d1 = self.d1()
        return -norm.cdf(-d1) 
    
    def gamma(self):
        d1 = self.d1()
        return norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        
    def vega(self):
        d1 = self.d1()
        return self.S * norm.pdf(d1) * np.sqrt(self.T)

    def theta_call(self):
        d1 = self.d1()
        d2 = self.d2()
        term1 = - (self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return term1 - term2

    def theta_put(self):
        d1 = self.d1()
        d2 = self.d2()
        term1 = - (self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
        return term1 + term2

