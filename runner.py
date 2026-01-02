# runner.py
from engine import CMEEngine, Black76
from backtester import TradeLifecycle
import pandas as pd

# 1. Setup Config
CONFIG = {
    'target_dte': 45,
    'short_delta': 0.20,
    'long_delta': 0.10,
    'stop_loss_r': 1.0,    # 2x total spread value (Loss of 1 unit of credit)
    'take_profit_r': 0.5   # Gain of 0.5 units of credit
}

# 2. Fetch Data (Placeholders - you'll connect your OHLCV/IV sources here)
# trades_df = get_trades_from_url(SHEET_URL)

def run_portfolio_backtest(trades_df, price_data_dict, iv_data_dict):
    lifecycle = TradeLifecycle(MARKET_SPECS)
    all_logs = []

    for _, row in trades_df.iterrows():
        market = row['Market']
        # Retrieve the specific price/IV dataframes for this market
        price_df = price_data_dict[market]
        iv_df = iv_data_dict[market]
        
        # Run the daily walk
        trade_log = lifecycle.run(
            market=market,
            entry_date=row['EntryDate'],
            direction=row['Direction'],
            price_df=price_df,
            iv_df=iv_df,
            config=CONFIG
        )
        all_logs.append(trade_log)
    
    return all_logs