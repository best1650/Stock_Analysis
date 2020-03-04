import os
import operator
import requests
import urllib.parse
import textwrap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import datetime
import time
import mplcursors
import json
import warnings
import pandas as pd

warnings.filterwarnings("ignore")

STOCK_API_URL = "https://api.twelvedata.com/"
STOCK_API_KEY = "e763a45b79a14e99983d22e08b10331a"
STOCK_INTERVAL = '1min'


def parseDate(dateTime):
    return datetime.datetime.strptime(dateTime, "%Y-%m-%d")

def getDailyStockData(symbol, cur_date, next_date):
    apiParams = {  \
        'format':"JSON",\
        'symbol':symbol,\
        'interval':STOCK_INTERVAL,\
        'apikey':STOCK_API_KEY,\
        'start_date':cur_date,\
        'end_date':next_date\
    }
    
    apiURL = STOCK_API_URL + "time_series?"
    resp = requests.get(url=apiURL, params=apiParams, verify=False);
    stockData = resp.json()

    if stockData['status'] == 'ok':
        priceList = []
        for dailyData in stockData['values']:
            priceList.insert(0, dailyData['open'])

        writeFile = open("dailyStockPrice/" + symbol + ".txt", "a")
        for price in priceList:
            writeFile.write(str(price) + ",")
        writeFile.write("\n")
        writeFile.close()
        print("Okay")
    else:
        print("Fail")
        

def downloadStockDataList(symbol):
    #newFile = open("dailyStockPrice/" + symbol + ".txt", "w")
    #newFile.close()
    
    start_date = parseDate('2020-02-26')
    end_date = parseDate('2020-03-01')
    
    while start_date <= end_date:
        if start_date.isoweekday() in range(1, 6):
            next_date = start_date + datetime.timedelta(days=1)
            print(start_date.strftime('%Y-%m-%d') + ".....", end='')
            getDailyStockData(symbol, start_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'))
            time.sleep(1)
        start_date = start_date + datetime.timedelta(days=1)
        
if __name__ == "__main__":
    downloadStockDataList('AMD')
    print("Completed!")




    
