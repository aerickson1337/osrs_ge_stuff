import requests
import json
from datetime import datetime
import pandas as pd
import time
import os

from dotenv import load_dotenv
load_dotenv()

def updateMapping():
    getDataFromEndpoint('mapping', filename='mapping.json')

def getDataFromEndpoint(endpoint, save=True, filename=None):
    url = f'http://prices.runescape.wiki/api/v1/osrs/{endpoint}'
    if not os.getenv("APP_NAME") or not os.getenv("CONTACT_INFO"):
        raise Exception('what the hell bro fill out the .env file')
    headers = {'User-Agent': f'{os.getenv("APP_NAME")} - {os.getenv("CONTACT_INFO")}'}

    data = requests.get(url, headers=headers).json()

    if save:
        if not filename:
            filename = f'{endpoint}_sample_{datetime.now().strftime("%d_%m_%Y-%H:%M:%S")}.json'
        with open(f'scripts/json/tmp/{filename}', 'w+') as writefile:
            writefile.write(json.dumps(data))
        print(f'saved file as: {filename}')

    return data

def latestItemsWithAction():
    latestData = getDataFromEndpoint('latest')
    with open('scripts/json/mapping.json', 'r') as readfile:
        latestMapping = json.load(readfile)

    dataIWant = []
    for item in latestMapping:
        itemMap = {}
        realtimeDataForItem = latestData.get('data', {}).get(f'{item["id"]}')
        if realtimeDataForItem:
            if int(item.get('limit', 0)) >= 50:
                timeDiff = abs(realtimeDataForItem.get('highTime') - realtimeDataForItem.get('lowTime'))
                if timeDiff <= (60*60) and int(item.get('highalch', 11)) <= 10:
                    itemMap['name'] = item.get('name')
                    itemMap['diff'] = realtimeDataForItem.get('high') - realtimeDataForItem.get('low')
                    itemMap['timeDiff'] = time.strftime('%H:%M:%S', time.gmtime(timeDiff))
                    itemMap['high'] = realtimeDataForItem.get('high')
                    itemMap['low'] = realtimeDataForItem.get('low')
                    itemMap['buyLimit'] = item.get('limit')
                    dataIWant.append(itemMap)

    df = pd.DataFrame.from_dict(dataIWant)
    df.to_csv('scripts/csv/test.csv', index=None)

if __name__ == "__main__":
    # updateMapping()
    # latestItemsWithAction()
    # with open('scripts/json/tmp/5m_sample_04_09_2021-21:53:30.json', 'r') as readfile:
    #     fiveMinData = json.load(readfile)
    fiveMinData = getDataFromEndpoint('5m')
    with open('scripts/json/tmp/mapping.json', 'r') as readfile:
        latestMapping = json.load(readfile)

    dataIWant = []
    for item in latestMapping:
        itemMap = {}
        realtimeDataForItem = fiveMinData.get('data', {}).get(f'{item["id"]}')
        if realtimeDataForItem:
            itemMap['name'] = item.get('name')
            itemMap['avgHighPrice'] = realtimeDataForItem.get('avgHighPrice')
            itemMap['avgLowPrice'] = realtimeDataForItem.get('avgLowPrice')
            if realtimeDataForItem.get('avgHighPrice') and realtimeDataForItem.get('avgLowPrice'):
                itemMap['diffPrice'] = realtimeDataForItem.get('avgHighPrice') - realtimeDataForItem.get('avgLowPrice')
                if itemMap['diffPrice']:
                    itemMap['magnitude'] = itemMap['diffPrice'] / ((realtimeDataForItem.get('avgHighPrice') + realtimeDataForItem.get('avgLowPrice')) / 2)
            itemMap['diffVolume'] = realtimeDataForItem.get('highPriceVolume') - realtimeDataForItem.get('lowPriceVolume')
            itemMap['highVolume'] = realtimeDataForItem.get('highPriceVolume')
            itemMap['lowVolume'] = realtimeDataForItem.get('lowPriceVolume')
            itemMap['time'] = datetime.fromtimestamp(fiveMinData.get('timestamp')).strftime("%d_%m_%Y-%H:%M:%S")
            itemMap['buyLimit'] = item.get('limit')
            dataIWant.append(itemMap)

    df = pd.DataFrame.from_dict(dataIWant)
    data = df['diffVolume']
    df.to_csv('scripts/csv/test2.csv', index=None)