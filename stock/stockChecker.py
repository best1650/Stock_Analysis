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

DATE_FORMAT = "%Y-%m-%d"
TODAY = datetime.datetime.today()
#TODAY = datetime.datetime.strptime("2020-02-26", DATE_FORMAT)
STOCK_API_URL = "https://api.twelvedata.com/"
STOCK_API_KEY = "e763a45b79a14e99983d22e08b10331a"
STOCK_START_DATE = TODAY.strftime(DATE_FORMAT)
STOCK_END_DATE = (TODAY + datetime.timedelta(days=1)).strftime(DATE_FORMAT)
STOCK_INTERVAL = '1min'
DOWN_HILL_TIME_LIMIT = 19
UP_HILL_TIME_LIMIT = 3

def downloadStockPriceList(symbol):
    apiParams = {  \
        'format':"JSON",\
        'symbol':symbol,\
        'interval':STOCK_INTERVAL,\
        'apikey':STOCK_API_KEY,\
        'start_date':STOCK_START_DATE,\
        'end_date':STOCK_END_DATE\
    }
    
    apiURL = STOCK_API_URL + "time_series?"
    resp = requests.get(url=apiURL, params=apiParams, verify=False);
    stockData = resp.json()

    stockPriceList = []
    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            stockPriceList.insert(0, float(dailyData['close']))
    return stockPriceList

def downloadStockEmaList(symbol):
    apiParams = {  \
        'format':"JSON",\
        'symbol':symbol,\
        'interval':STOCK_INTERVAL,\
        'apikey':STOCK_API_KEY,\
        'start_date':STOCK_START_DATE,\
        'end_date':STOCK_END_DATE,\
        'time_period':10
    }
    
    apiURL = STOCK_API_URL + "ema?"
    resp = requests.get(url=apiURL, params=apiParams, verify=False);
    stockData = resp.json()

    stockEmaList = []
    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            stockEmaList.insert(0, float(dailyData['ema']))
    return stockEmaList

def stockTraining(stockPriceList):
    maxPrice = 0.0
    maxPriceIdx = -1
    downHillCounter = 0
    upHillCounter = 0

    for stockIdx, stockPrice in enumerate(stockPriceList):
        isDownHill = False
        print(str(stockIdx) + " - ", end='')
        if stockPrice > maxPrice:
            if  (maxPrice == 0) or (((stockPrice - maxPrice) / maxPrice) > 0.5):
                print("New max price")
                maxPrice = stockPrice
                maxPriceIdx = stockIdx
                downHillCounter = 0
                upHillCounter = 0
            else:
                isDownHill = True
        else:
            isDownHill = True

        if isDownHill:
            print("Down hill")
            downHillCounter += 1
            if downHillCounter > DOWN_HILL_TIME_LIMIT:
                print("Test time")
                preStockPrice = stockPriceList[(stockIdx-1)]
                if stockPrice > preStockPrice:
                    return stockIdx, stockPrice

    return -1, 0.0

def drawGraph(symbol, stockPriceList, lowIdx, lowPrice):
    fig, ax = plt.subplots()
    x = list(range(0, len(stockPriceList)))
    fig.set_size_inches(15,8)
    plt.title(symbol + " Stock Trend", fontsize=24)
    plt.xlabel("Time", fontsize=18)
    plt.ylabel("Stock Price", fontsize=18)
    ax.plot(x, stockPriceList, 'r-')
    plt.plot(lowIdx, lowPrice, 'go')
    #plt.hlines((lowPrice * 1.015), 0, len(stockPriceList), colors = 'k', label = str(lowPrice))
    fmt = mplcursors.cursor(hover=True)
    plt.show()

def drawGraphWithEMA(symbol, stockPriceList, stockEmaList):
    fig, ax = plt.subplots()
    x = list(range(0, len(stockPriceList)))
    fig.set_size_inches(15,8)
    plt.title(symbol + " Stock Trend", fontsize=24)
    plt.xlabel("Time", fontsize=18)
    plt.ylabel("Stock Price", fontsize=18)
    ax.plot(x, stockPriceList, 'r-')
    ax.plot(x, stockEmaList, 'g-')
    #plt.hlines((lowPrice * 1.015), 0, len(stockPriceList), colors = 'k', label = str(lowPrice))
    fmt = mplcursors.cursor(hover=True)
    plt.show()

def stockTesting(stockList):
    for stock in stockList:
        symbol = stock
        stockPriceList = downloadStockPriceList(symbol)
        #stockEmaList = downloadStockEmaList(symbol)
        #for x in range (0, len(stockPriceList), 5):
        lowIdx, lowPrice = stockTraining(stockPriceList)
        drawGraph(symbol, stockPriceList, lowIdx, lowPrice)
        #drawGraph(symbol, stockPriceList[:x], stockEmaList[:x])

 
if __name__ == "__main__":
    #stockList = ["AMD", "LRCX", "NVDA", "MSFT", "INTC", "NOW", "AMZN", "AAPL", "TSLA", "PYPL", "MA", "V", "DAL", "UAL", "COST", "WMT"]
    stockList = ["INTC"]
    stockTesting(stockList)
    print("Complete!")

    
    
