import datetime as dt
import pandas as pd
import schedule
from schedule import *
from pandas_datareader import data as pdr
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import requests
from websocket import create_connection
import simplejson as json
import json
from tiingo import TiingoClient
from scipy.signal import argrelextrema
import numpy as np
import urllib
import bs4
import pyEX
import csv
import os

today = dt.date.today()

df = pd.read_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/top_loser_list_{today}.csv')
top_loser_list = df['ticker'].values.tolist()

#scan premarket
def first_red_day():
    first_red_day = []
    for ticker in top_loser_list:
        try:
            iexresponse = requests.get(
                f"https://cloud.iexapis.com/stable/stock/{ticker}/chart/4d?token=sk_00fa84b3b1664e30a5257d8929bea0f3")
            data = iexresponse.json()
            change = []
            for i in data:
                change.append(i['changePercent'])
            print(change, ticker)
            total_gain = round(data[2]['changeOverTime'], 3)
            current_price = data[3]['close']
            print(total_gain, ticker)
            if all(x > 0 for x in change[1:]):
                if total_gain >= 0.5:
                    if current_price > 1.5:
                        first_red_day.append(ticker)
                    else:
                        pass
        except:
            print("No data on ticker", ticker)

    print("first red day: ", first_red_day)


if __name__ == '__main__':
    first_red_day()
