import requests
from tiingo import TiingoClient
import pandas as pd
import simplejson as json

config = {'session': True, 'api_key': "e7aac5df98ef4e167db7fdc478ad2d6d7470761d"}
client = TiingoClient(config)


def REST():
    headers = {'Content-Type': 'application/json'}
    requestResponse = requests.get(
        "https://api.tiingo.com/iex/?token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
        headers=headers)
    data = requestResponse.json()


if __name__ == '__main__':
    REST()
    tickers = client.list_stock_tickers()
    ticker_names = [stock['ticker'] for stock in tickers if
                    not stock['exchange'] == 'SHE' and not stock['exchange'] == 'SHG']
    dict = {'ticker': ticker_names}

    US_listed = pd.DataFrame(dict)
    US_listed.to_csv(r'/Users/kwunyingzhou/Downloads/PyScreener/screener/cache/US_listed.csv', index=False)
