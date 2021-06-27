import pytrendline
import datetime as dt
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import bokeh
import colour
import os

yf.pdr_override()
start = dt.datetime(2020, 1, 1)
now = dt.datetime.now()

df = pdr.get_data_yahoo('aapl', start, now)

candles_df = pd.DataFrame(df)
candles_df['Date'] = pd.to_datetime(candles_df['Date'])

candlestick_data = pytrendline.CandlestickData(
    df=candles_df,
    time_interval="1d",  # choose between 1m,3m,5m,10m,15m,30m,1h,1d
    open_col="Open",  # name of the column containing candle "Open" price
    high_col="High",  # name of the column containing candle "High" price
    low_col="Low",  # name of the column containing candle "Low" price
    close_col="Close",  # name of the column containing candle "Close" price
    datetime_col='Date'  # name of the column containing candle datetime price (use none if datetime is in index)
)

results = pytrendline.detect(
    candlestick_data=candlestick_data,

    # Choose between BOTH, SUPPORT or RESISTANCE
    trend_type=pytrendline.TrendlineTypes.RESISTANCE,
    # Specify if you require the first point of a trendline to be a pivot
    first_pt_must_be_pivot=False,
    # Specify if you require the last point of the trendline to be a pivot
    last_pt_must_be_pivot=False,
    # Specify if you require all trendline points to be pivots
    all_pts_must_be_pivots=False,
    # Specify if you require one of the trendline points to be global max or min price
    trendline_must_include_global_maxmin_pt=False,
    # Specify minimum amount of points required for trendline detection (NOTE: must be at least two)
    min_points_required=3,
    # Specify if you want to ignore prices before some date
    scan_from_date=None,
    # Specify if you want to ignore 'breakout' lines. That is, lines that interesect a candle
    ignore_breakouts=True,
    # Specify and override to default config (See docs on how)
    config={}
)

outf = pytrendline.plot(
    results=results,
    filedir='.',
    filename='example_output.html',
)

os.system("open " + outf)
