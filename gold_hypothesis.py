# %%
#   lib import
import yfinance as yf, pandas as pd, numpy as np

# %%
#Get data and combine into one DF

tickers = ['GC=F', '^GSPC']
df_union = pd.DataFrame()

for ticker in tickers:
    #   Get historical data from tickers
    raw_data = yf.download(ticker, start='1900-01-01', end= '2024-12-31')
    df = raw_data['Close'].reset_index()

    #   Filtering only one day of the week
    df['Date'] = pd.to_datetime(df['Date'])
    df['DOW'] = df['Date'].dt.day_name()
    df = df[df['DOW'] == 'Monday']

    #   Naming/Creating identification columns
    df = df.rename(columns={ticker: 'Price'})
    df['Ticker'] = ticker

    #   Comparing WoW Price
    df['PriceLag'] = df.groupby(['Ticker'])['Price'].shift(1)
    df['PriceDiff'] = df['Price'] - df['PriceLag']
    df['IsPositive'] = np.where(df['PriceDiff'] > 0, 1, 0)
    

    #   Rearranging columns
    df = df[['Date', 'Ticker', 'IsPositive']]

    if(df_union.shape[1] > 0):
        df_union = df_union.merge(df, how='left', on='Date')
    else:
        df_union = df

# %%
df_union
# %%
