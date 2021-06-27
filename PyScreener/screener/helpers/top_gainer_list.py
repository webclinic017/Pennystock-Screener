import requests
import datetime as dt
import schedule
from schedule import *
from tiingo import TiingoClient
import pandas as pd
import simplejson as json

today = dt.date.today()

config = {'session': True, 'api_key': "e7aac5df98ef4e167db7fdc478ad2d6d7470761d"}
client = TiingoClient(config)

headers = {'Content-Type': 'application/json'}
requestResponse = requests.get(
    "https://api.tiingo.com/iex/?token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
    headers=headers)
data = requestResponse.json()


# need to be updated everyday --> cache(update)
def get_top_gainer():
    dict = []
    data = requestResponse.json()

    for ticker in data:
        try:
            pct_change = ((ticker['tngoLast'] - ticker['prevClose']) / ticker['prevClose']) * 100
            if pct_change >= 40:
                dict.append({'ticker': ticker['ticker'], 'percent change(%)': round(pct_change, 3)})
        except:
            pass
    return dict

def daily_update():
    schedule.every().day.at("20:00").do(get_top_gainer)
    schedule.every().day.at("20:30").do(get_top_gainer)
    schedule.every().day.at("21:00").do(get_top_gainer)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    dict = get_top_gainer()
    df = pd.DataFrame(dict, columns= ['ticker', 'percent change(%)'])
    df.to_csv(fr'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/daily_update/top_gainer_list_{today}.csv',
              index=False)

