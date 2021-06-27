import datetime as dt
import pandas as pd
import schedule
from schedule import *
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import requests
from websocket import create_connection
import simplejson as json
from tiingo import TiingoClient
from bs4 import BeautifulSoup
from scipy.signal import argrelextrema
from collections import defaultdict
import numpy as np
import urllib
import bs4
import pyEX
import csv
import os



today = dt.date.today()
now = dt.datetime.now()
print(now)

# Tiingo Initialize
config = {'session': True, 'api_key': "76d847b87f82c87be5007eaafa6eaeebb07d5b1b"}
client = TiingoClient(config)
headers = {'Content-Type': 'application/json'}
requestResponse = requests.get("https://api.tiingo.com/iex/?token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",headers=headers)

# iexcloud Initialize

pyEX.Client(api_token='76d847b87f82c87be5007eaafa6eaeebb07d5b1b')

df = pd.read_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/top_gainer_list_{today}.csv')
top_gainer_list = df['ticker'].values.tolist()
ticker_dict ={}

def filter_MarketCap():
    backup_list1 = []
    marketCapData = {}
    iexresponse = requests.get(
        "https://cloud.iexapis.com/stable/stock/market/batch?symbols={}&types=quote&token=sk_00fa84b3b1664e30a5257d8929bea0f3".format(
            ','.join(top_gainer_list)))
    data = iexresponse.json()
    for ticker in top_gainer_list:
        try:
            marketCap = int(data[ticker]['quote']['marketCap'])
            if 10000000 <= marketCap <= 200000000:
                cond_1 = True
            else:
                cond_1 = False
            marketCapData[ticker] = {'marketCap': marketCap, 'cond_1': cond_1}
            ticker_dict[ticker] = {'marketCap': marketCap, 'cond_1': cond_1}
        except:
            backup_list1.append(ticker)
            ticker_dict[ticker] = {'marketCap': 'N/A', 'cond_1': 'N/A'}
    print("Market cap data not available: ", backup_list1)
    return marketCapData


def get_market_cap():
    ticker = input("Please enter ticker symbol: ")
    try:
        iexresponse = requests.get(
            f"https://cloud.iexapis.com/stable/stock/{ticker}/stats/marketcap?token=sk_00fa84b3b1664e30a5257d8929bea0f3")
        marketCap = int(iexresponse.json())
        print(ticker + ": ", marketCap)
    except:
        print("Cannot find marketcap for ticker ", ticker)


def parseFloat():
    get_top_gainer()
    for ticker in top_gainer_list:
        try:
            response = requests.get(f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}",
                                        headers={"User-Agent": 'Mozilla/5.0'})
            soup = bs4.BeautifulSoup(response.content, "lxml")
            table = soup.find_all('table', {'class': 'W(100%) Bdcl(c)'})
            table_rows = table[3].find_all('tr')
            float = table_rows[4].find_all('td')[1].text
            if float == 'N/A':
                print("Error: Cannot find float for ", ticker)
            else:
                print(ticker + ": ", float)
        except:
            print("Error: Cannot find float for ", ticker)

def filter_SharesFloat():
    floatData = {}
    backup_list2 = []
    for ticker in top_gainer_list:
        try:
            response = requests.get(f"https://eodhistoricaldata.com/api/fundamentals/{ticker}.US?filter=SharesStats::SharesFloat&api_token=60c6e518b87e52.21334087")
            data = response.json()
            SharesFloat = int(data)
            if SharesFloat == 0:
                backup_list2.append(ticker)
            else:
                print(ticker + ": ", SharesFloat)
                if 2000000 <= SharesFloat <= 60000000:
                    cond_2 = True
                else:
                    cond_2 = False
                floatData[ticker] = {'float': SharesFloat, 'cond_2': cond_2}
                ticker_dict[ticker].update({'float': SharesFloat, 'cond_2': cond_2})
        except:
            backup_list2.append(ticker)
        for ticker in backup_list2:
            ticker_dict[ticker].update({'float': 'N/A', 'cond_2': 'N/A'})
    exportFloat = pd.DataFrame(floatData)
    exportFloat.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/exportFloat_{today}.csv')

    print("Float data not available: ", backup_list2)

def filter_last_price():
    backuplist3 = []
    priceData = {}
    data = requestResponse.json()
    for gainer in top_gainer_list:
        for ticker in data:
            if gainer == ticker['ticker']:
                try:
                    price = ticker['tngoLast']
                    if 1.5 <= price:
                        cond_3 = True
                    else:
                        cond_3 = False
                    priceData[ticker['ticker']] = {'last price': price, 'cond_3': cond_3}
                    ticker_dict[ticker['ticker']].update({'last price': price, 'cond_3': cond_3})
                except:
                    ticker_dict[ticker['ticker']].update({'last price': 'N/A', 'cond_3': 'N/A'})
                    backuplist3.append(ticker)
                    pass
        else:
            pass
    return priceData

def filter_last_volume(): # type:
    premarketVolumeData = {}
    backuplist4 = []
    data = requestResponse.json()
    for gainer in top_gainer_list:
        for ticker in data:
            if gainer == ticker['ticker']:
                try:
                    last_volume = ticker['volume']
                    if 100000 <= last_volume <= 4000000:
                        cond_4 = True
                    else:
                        cond_4 = False
                    premarketVolumeData[ticker['ticker']] = {'volume': last_volume, 'cond_4': cond_4,
                                            'predicted intraday volume': last_volume * 4}
                    ticker_dict[ticker['ticker']].update({'volume': last_volume, 'cond_4': cond_4, 'predicted intraday volume': last_volume * 4})

                except:
                    backuplist4.append(ticker)
                    ticker_dict[ticker['ticker']] = {'volume': 'N/A', 'cond_4': 'N/A',
                                            'predicted intraday volume': 'N/A'}
                    pass
            else:
                pass
    df = pd.DataFrame(premarketVolumeData)
    df.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/premarket_volume_{today}.csv',
              index=True)



def filter_float_rotation():
    floatRotationData = {}
    backuplist5 = []
    readFloat = pd.read_csv(
        fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/exportFloat_{today}.csv', index_col=0)
    floatData = readFloat.to_dict(orient='dict')

    readVolume = pd.read_csv(
        fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/premarket_volume_{today}.csv',
        index_col=0)
    volumeData = readVolume.to_dict(orient='dict')

    a = set(volumeData)
    b = set(floatData)
    c = a.intersection(b)
    d = a.symmetric_difference(b)

    for ticker in c:
        floatRotation = round(
            (float(volumeData[ticker]['predicted intraday volume']) / float(floatData[ticker]['float'])), 2)
        if floatRotation < 1:
            cond_5 = True
        else:
            cond_5 = False
        ticker_dict[ticker].update({'float rotation': floatRotation, 'cond_5': cond_5})

    df = pd.DataFrame(floatRotationData)
    df.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/float_rotation_{today}.csv',
              index=True)

    for ticker in d:
        ticker_dict[ticker].update({'float rotation': 'N/A', 'cond_5': 'N/A'})
def filter_double_resistance(): # type:
    doubleResistanceData = {}
    backuplist6 = []
    data = requestResponse.json()
    for gainer in top_gainer_list:
        for ticker in data:
            if gainer == ticker['ticker']:
                try:
                    last_volume = ticker['volume']
                    if last_volume >= 4000000:
                        cond_6 = True
                    else:
                        cond_6 = False
                        doubleResistanceData[ticker['ticker']] = {'premarket volume': last_volume, 'cond_6': cond_6, 'predicted intraday volume': last_volume * 10}
                except:
                    backuplist6.append(ticker)
                    pass
            else:
                pass
    return doubleResistanceData


def main():
    filter_MarketCap()
    filter_SharesFloat()
    filter_last_price()
    filter_last_volume()
    filter_float_rotation()
    gap_up_short = []
    filter_marketCap = []
    filter_float = []
    filter_price = []
    filter_volume = []
    filter_rotation = []

    for ticker in top_gainer_list:
        if ticker_dict[ticker]['cond_1'] and ticker_dict[ticker]['cond_2'] and ticker_dict[ticker]['cond_3'] and ticker_dict[ticker]['cond_4'] and ticker_dict[ticker]['cond_5'] == True:
            gap_up_short.append(ticker)
        if ticker_dict[ticker]['cond_1'] == True:
            filter_marketCap.append(ticker)
        if ticker_dict[ticker]['cond_2'] == True:
            filter_float.append(ticker)
        if ticker_dict[ticker]['cond_3'] == True:
            filter_price.append(ticker)
        if ticker_dict[ticker]['cond_4'] == True:
            filter_volume.append(ticker)
        if ticker_dict[ticker]['cond_5'] == True:
            filter_rotation.append(ticker)
        else:
            pass

    print("filter by market cap: ", filter_marketCap)
    print("filter by float: ", filter_float)
    print("filter by price: ", filter_price)
    print("filter by volume: ", filter_volume)
    print("filter by float rotation: ", filter_rotation)

    print(gap_up_short)
    df = pd.DataFrame(ticker_dict)
    df.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/top_gainer_data_{today}.csv',
              index=True)

    if len(gap_up_short) != 0:
        final_export = requests.get(
            'https://cloud.iexapis.com/stable/stock/market/batch?symbols={}&types=quote&token=sk_00fa84b3b1664e30a5257d8929bea0f3'.format(
                ','.join(gap_up_short)))
        data = final_export.json()
        df = pd.DataFrame.from_dict({(i, j): data[i][j]
                                     for i in data.keys()
                                     for j in data[i].keys()}, orient='index')
        df.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/gap_up_short/{today}.csv')


def filter_close_to_resistance():
    df = pd.read_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/gap_up_short/{today}.csv')
    gap_up_short = [i for i in df['symbol'].values.tolist()]
    bounce_short = []
    for ticker in gap_up_short:
        eodRequestResponse = requests.get(
            f"https://cloud.iexapis.com/stable/stock/{ticker}/chart/1y?token=sk_00fa84b3b1664e30a5257d8929bea0f3")
        data = eodRequestResponse.json()
        df = pd.DataFrame(data)

        np.random.seed(0)
        rs = np.random.randn(200)
        xs = [0]
        for r in rs:
            xs.append(xs[-1] * 0.9 + r)

        n = 5

        df['max'] = df.iloc[argrelextrema(df.high.values, np.greater_equal,
                                          order=n)[0]]['high']

        print(df['max'])

        isPivot = df['max'].notnull()
        pivots = [x for x in df[isPivot]['max']]
        pivotDates = [x for x in df[isPivot]['label']]
        pivotVolumes = [x for x in df[isPivot]['volume']]


        pivotDatesData = dict(zip(pivots, pivotDates))
        print(pivotDatesData)

        pivotVolumesData = dict(zip(pivots, pivotVolumes))

        plt.scatter(df.index, df['max'], c='g')
        plt.plot(df.index, df['high'])
        plt.show()

        headers = {
            'Content-Type': 'application/json'
        }
        requestResponse = requests.get(
            f"https://api.tiingo.com/iex/?tickers={ticker}&token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
            headers=headers)

        data = requestResponse.json()
        last_price = data[0]['tngoLast']
        last_volume = data[0]['volume']
        for i in pivots:
            if  0.7 * i <= last_price < i:
                print("current price close to pivot", i, pivotDatesData[i], pivotVolumesData[i])
                if pivotVolumesData[i] >= last_volume * 10:
                    print("pivot resistance" + i + "satisfies volume condition")
                    bounce_short.append(ticker)
                else:
                    pass
            else:
                print("current price not close to pivot", i)
                pass
    print(bounce_short)





if __name__ == '__main__':
    main()
