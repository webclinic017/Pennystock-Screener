import requests
from tiingo import TiingoClient
from websocket import create_connection
import simplejson as json

config = {'session': True, 'api_key': "e7aac5df98ef4e167db7fdc478ad2d6d7470761d"}
client = TiingoClient(config)


def REST():
    headers = {'Content-Type': 'application/json'}
    requestResponse = requests.get(
        "https://api.tiingo.com/iex/?token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b",
        headers=headers)
    data = requestResponse.json()


def websocket():
    ws = create_connection("wss://api.tiingo.com/iex/?token=76d847b87f82c87be5007eaafa6eaeebb07d5b1b")

    subscribe = {
        'eventName': 'subscribe',
        'authorization': 'e7aac5df98ef4e167db7fdc478ad2d6d7470761d',
        'eventData': {
            'thresholdLevel': 5
        }
    }

    ws.send(json.dumps(subscribe))
    while True:
        print(ws.recv())
