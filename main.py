import pandas as pd
import os
from engine import CMEEngine
from backtester import TradeLifecycle
from runner import CONFIG, MARKET_SPECS

# 1. DATA LOADER UTILITY
def load_local_data(market):
    """Loads Price and IV CSVs from the /data folder."""
    try:
        price_path = f"data/{market}_price.csv"
        iv_path = f"data/{market}_iv.csv"
        
        price_df = pd.read_csv(price_path, index_index=False)
        price_df['Date'] = pd.to_datetime(price_df['Date'])
        price_df.set_index('Date', inplace=True)
        
        iv_df = pd.read_csv(iv_path, index_index=False)
        iv_df['Date'] = pd.to_datetime(iv_df['Date'])
        iv_df.set_index('Date', inplace=True)
        
        return price_df, iv_df
    except FileNotFoundError:
        print(f"Warning: Data for {market} not found in /data folder.")
        return None, None

# 2. SECTOR MAPPING
SECTOR_MAP = {
    'ES': 'Equity', 'NQ': 'Equity', 'RTY': 'Equity',
    'CL': 'Energy', 'NG': 'Energy',
    'ZC': 'Agriculture', 'ZS': 'Agriculture', 'ZW': 'Agriculture',
    '6E': 'Currency', '6J': 'Currency',
    'ZB': 'Financials'
}

def main():
    # A. Fetch trades from your Public Google Sheet URL
    # Replace with your actual Published CSV link
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAag95ldphXrtCXAg_9EFTBnmvo0MqgF6ROUPkGtKwnP6R1BB04CvS2wvKgaUDz2SbgKQF8PjYM50g/pub?gid=0&single=true&output=csv"
    trades_input = pd.read_csv(SHEET_URL)
    trades_input['EntryDate'] = pd.to_datetime(trades_input['EntryDate'])

    lifecycle = TradeLifecycle(MARKET_SPECS)
    all_results = []

    # B. Process each trade
    for idx, row in trades_input.iterrows():
        market = row['Market']
        print(f"Processing {market} trade entered on {row['EntryDate'].date()}...")
        
        # Load the market-specific CSVs
        price_df, iv_df = load_local_data(market)
        
        if price_df is not None and iv_df is not None:
            # Run the backtest
            trade_log = lifecycle.run(
                market=market,
                entry_date=row['EntryDate'],
                direction=row['Direction'],
                price_df=price_df,
                iv_df=iv_df,
                config=CONFIG
            )
            
            # Tag with metadata for the dashboard
            trade_log['Market'] = market
            trade_log['Sector'] = SECTOR_MAP.get(market, 'Other')
            trade_log['Trade_ID'] = f"{market}_{idx}"
            
            all_results.append(trade_log)

    # C. Aggregate and Save
    if all_results:
        final_df = pd.concat(all_results)
        # Save to a master file that dashboard.py will read
        final_df.to_csv("backtest_results.csv", index=False)
        print("Backtest complete. Results saved to backtest_results.csv")
    else:
        print("No trades were processed.")

if __name__ == "__main__":
    main()