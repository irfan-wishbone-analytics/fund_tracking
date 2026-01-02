import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import pandas_market_calendars as mcal

class Black76:
    @staticmethod
    def calculate_greeks(F, K, T, sigma, r, option_type='put'):
        if T <= 0: return {"price": 0, "delta": 0}
        d1 = (np.log(F / K) + (0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        discount = np.exp(-r * T)
        if option_type.lower() == 'call':
            price = discount * (F * norm.cdf(d1) - K * norm.cdf(d2))
            delta = discount * norm.cdf(d1)
        else:
            price = discount * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
            delta = -discount * norm.cdf(-d1)
        return {"price": price, "delta": delta}

    @staticmethod
    def find_strike(F, target_delta, T, sigma, market, option_type='put'):
        increments = {'ES': 5, 'NQ': 25, 'CL': 0.5, 'GC': 10, 'ZC': 5, '6E': 0.005}
        inc = increments.get(market, 1)
        # Scan a range around the underlying
        strikes = np.arange(F * 0.5, F * 1.5, inc / 10) # Fine-grained scan
        best_k, min_diff = F, float('inf')
        for k in strikes:
            valid_k = round(k / inc) * inc
            delta = abs(Black76.calculate_greeks(F, valid_k, T, sigma, 0.04, option_type)['delta'])
            if abs(delta - target_delta) < min_diff:
                min_diff = abs(delta - target_delta)
                best_k = valid_k
        return best_k

class CMEEngine:
    def __init__(self):
        try: self.cal = mcal.get_calendar('CME_Equity')
        except: self.cal = mcal.get_calendar('CME Globex Equity')
        self.codes = {1:'F', 2:'G', 3:'H', 4:'J', 5:'K', 6:'M', 7:'N', 8:'Q', 9:'U', 10:'V', 11:'X', 12:'Z'}

    def get_expiry(self, market, ref_date, target_dte=45):
        ref_dt = pd.Timestamp(ref_date).tz_localize(None)
        target_dt = ref_dt + timedelta(days=target_dte)
        y, m = target_dt.year, target_dt.month
        # Simplification of logic built previously
        first_day = pd.Timestamp(year=y, month=m, day=1)
        expiry = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7) + timedelta(weeks=2)
        return expiry.tz_localize(None)