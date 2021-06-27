import datetime as dt
import time
import schedule
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from bs4 import beautifulsoup
import bs4

#will not read if not updated data from today
today = dt.date.today()
print(today)
df = pd.read_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/top_gainer_list{today}.csv')
top_gainer_list = df['ticker'].values.tolist()

# Bounce Short
#filter by percent change since last close to get gainers for bounce short (>= 50% gap-up pre market)
## need to be updated everyday --> cache(update)


#filter by market cap
#Max 100 quotes at one time(source: iexCloud)
# Condition 1: Market Cap > 20M and < 100M
## need to be updated everyday --> cache(update)
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
        except:
            backup_list1.append(ticker)
    print("Market cap data not available: ", backup_list1)
    return marketCapData


# One quote at a time(source: EOD)
# Condition 2: Float > 2M and < 30M
## need to be updated everyday --> cache(update)
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


def filter_premarket_volume():
    # run with nohup in command ("nohup python3 filename.py")
    schedule.every().day.at("20:00").do(filter_last_volume)
    schedule.every().day.at("20:40").do(filter_last_volume)
    schedule.every().day.at("21:15").do(filter_last_volume)

    while True:
        schedule.run_pending()
        time.sleep(60)  # wait one minute


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





# Condition 5: Float rotations: Predicted Intra-day Volume / Float < 1
# Condition_5 = predictedVolume / floatShares < 1
def get_predicted_intra_volume():
    # Intra-day Volume Prediction = Premarket Volume * 10 or First-Hour Volume * 4
    ticker = input("Enter ticker symbol(before market open): ")
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        requestResponse = requests.get(
            f"https://api.tiingo.com/iex/?tickers={ticker}&token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
            headers=headers)

        data = requestResponse.json()
        predicted_intra_volume = data[0]['volume'] * 10
        print("predicted intraday volume: ", predicted_intra_volume)
    except:
        print("Error: Cannot find predicted volume for ticker.")

##get info on single tickers (previous close, last price, last volume)
def get_prevClose():
    ticker = input("Enter ticker symbol:")
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        requestResponse = requests.get(
            f"https://api.tiingo.com/iex/?tickers={ticker}&token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
            headers=headers)

        data = requestResponse.json()
        prevClose = data[0]['prevClose']
        print("Previous close: ", prevClose)
    except:
        print("Error: Cannot find previous close for ticker.")


def get_last_price():
    ticker = input("Enter ticker symbol:")
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        requestResponse = requests.get(
            f"https://api.tiingo.com/iex/?tickers={ticker}&token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
            headers=headers)

        data = requestResponse.json()
        last_price = data[0]['tngoLast']
        print("Last price: ", last_price)
    except:
        print("Error: Cannot find last price for ticker.")


def get_last_volume():
    ticker = input("Enter ticker symbol:")
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        requestResponse = requests.get(
            f"https://api.tiingo.com/iex/?tickers={ticker}&token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
            headers=headers)

        data = requestResponse.json()
        last_volume = data[0]['volume']
        print("Last volume: ", last_volume)
    except:
        print("Error: Cannot locate volume for ticker.")

    # Resistance: Current Price is within 30% of the resistance level (getting close to resistance)
    ## a. find dates of historical resistance for selected tickers with yahoo finance
    ## b. store the dates as a list
    ## c. find price on the chosen dates
    ## d. select ticker if current close * 0.7 >= resistance price
    # get last price from Tiingo








if __name__ == '__main__':
    main()