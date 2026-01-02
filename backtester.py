import pandas as pd
class TradeLifecycle:
    # The URL you copied from "Publish to Web"
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAag95ldphXrtCXAg_9EFTBnmvo0MqgF6ROUPkGtKwnP6R1BB04CvS2wvKgaUDz2SbgKQF8PjYM50g/pub?gid=0&single=true&output=csv"

    def get_trades_from_url(url):
        try:
            # Pandas reads the CSV directly from the public URL
            df = pd.read_csv(url)
            
            # Standardize dates for our engine
            df['EntryDate'] = pd.to_datetime(df['EntryDate'])
            return df
        except Exception as e:
            print(f"Error fetching sheet: {e}")
            return None
    
    def __init__(self, specs):
        self.specs = specs # Dict of multipliers

    def run(self, market, entry_date, direction, price_df, iv_df, config):
        expiry = CMEEngine().get_expiry(market, entry_date, config['target_dte'])
        
        # Entry Data
        f_entry = price_df.loc[entry_date, 'Close']
        iv_entry = iv_df.loc[entry_date, 'IV']
        t_entry = (expiry - pd.Timestamp(entry_date)).days / 365
        
        # Find Strikes
        short_k = Black76.find_strike(f_entry, config['short_delta'], t_entry, iv_entry, market, direction)
        long_k = Black76.find_strike(f_entry, config['long_delta'], t_entry, iv_entry, market, direction)
        
        # Initial Credit
        s_p = Black76.calculate_greeks(f_entry, short_k, t_entry, iv_entry, 0.04, direction)['price']
        l_p = Black76.calculate_greeks(f_entry, long_k, t_entry, iv_entry, 0.04, direction)['price']
        initial_credit = (s_p - l_p) * 0.98 # Slippage
        
        log = []
        mask = (price_df.index >= entry_date) & (price_df.index <= expiry)
        for date, row in price_df.loc[mask].iterrows():
            days_left = (expiry - date).days
            t = max(days_left, 0.5) / 365
            iv = iv_df.loc[date, 'IV']
            
            # Current value (Close)
            curr_s = Black76.calculate_greeks(row['Close'], short_k, t, iv, 0.04, direction)['price']
            curr_l = Black76.calculate_greeks(row['Close'], long_k, t, iv, 0.04, direction)['price']
            spread_close = curr_s - curr_l
            
            pnl_r = (initial_credit - spread_close) / initial_credit
            
            log.append({'Date': date, 'Underlying': row['Close'], 'PnL_R': pnl_r})
            
            # Exit Logic
            if pnl_r <= -config['stop_loss_r']: break
            if pnl_r >= config['take_profit_r']: break
            
        return pd.DataFrame(log)