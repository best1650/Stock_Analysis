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
ONE_YEAR = 52
ONE_MONTH = 4
DATE_FORMAT = "%Y-%m-%d"
TODAY = datetime.datetime.today()
STOCK_API_URL = "https://api.twelvedata.com/"
STOCK_API_KEY = "e763a45b79a14e99983d22e08b10331a"
STOCK_END_DATE = TODAY.strftime(DATE_FORMAT)
STOCK_START_DATE = (TODAY - datetime.timedelta(weeks=ONE_YEAR * 2)).strftime(DATE_FORMAT)
STOCK_INTERVAL = '1day'

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
            stockPrice = {}
            stockPrice['datetime'] = dailyData['datetime']
            stockPrice['open'] = float(dailyData['open'])
            stockPrice['high'] = float(dailyData['high'])
            stockPrice['low'] = float(dailyData['low'])
            stockPrice['close'] = float(dailyData['close'])
            stockPriceList.insert(0, stockPrice)
    return stockPriceList

def findStockPattern(stockPriceList, expectDropRate, soarPeriod):
    numOfDrop = 0
    numOfRaiseAfterDrop = 0
    numOfStockDay = len(stockPriceList)
    
    for idx, stock in enumerate(stockPriceList):
        if (idx + soarPeriod + 2) > numOfStockDay:
            break
        
        prevPrice = stockPriceList[idx]['close']
        curPrice = stockPriceList[idx+1]['open']
        curAvgPrice = (stockPriceList[idx+1]['high'] + stockPriceList[idx+1]['low']) / 2
        #curAvgPrice = stockPriceList[idx+1]['low']
        curDate = stockPriceList[idx+1]['datetime']
        totalEarning = 0.0

        if curPrice < prevPrice:
            curDropRate = (prevPrice - curPrice) / prevPrice
            if curDropRate >= expectDropRate:
                numOfDrop += 1
                #print("Date:" + curDate)
                #print("Yesterday's Stock Close Price:" + str(prevPrice))
                #print("Today's Stock Open Price:" + str(curPrice))
                #print("Today's Stock Low Price:" + str(stockPriceList[idx+1]['low']))
                #print("Buy-in Price:" + str(curAvgPrice))
                #print("Drop Rate:%.4f"%curDropRate)
                for i in range(2, soarPeriod + 2):
                    nextDayPrice = stockPriceList[idx+i]['high']
                    if nextDayPrice > curAvgPrice:
                        totalEarning += ((nextDayPrice - curAvgPrice) / curAvgPrice);
                        numOfRaiseAfterDrop += 1
                        break
                #print("Next Day High Price:", end="")
                for i in range(2, soarPeriod + 2):
                    nextDayPrice = stockPriceList[idx+i]['high']
                    #print("%.2f  "%(nextDayPrice), end="")
                #print("\n")

    print("Total Stock Day:%d, Number of Drop Days:%d, Number of Soar Chance:%d, Earning:%.2f\n"%\
          (numOfStockDay, numOfDrop, numOfRaiseAfterDrop, totalEarning))

def findStockDropPattern(stockPriceList, expectDropRate):
    numOfDrop = 0
    nextDayDrop = 0
    for idx, stock in enumerate(stockPriceList):
        if idx+3 > len(stockPriceList):
            break
        
        prevDate = stockPriceList[idx]['datetime']
        prevPrice = stockPriceList[idx]['close']
        curDate = stockPriceList[idx+1]['datetime']
        curPrice = stockPriceList[idx+1]['open']
        if curPrice < prevPrice:
            curDropRate = (prevPrice - curPrice) / prevPrice
            if curDropRate >= expectDropRate:
                numOfDrop += 1
                print("Previous Date:%s -> %.2f" % (prevDate, prevPrice))
                print("Current Date:%s -> %.2f (low:%.2f)" % (curDate, curPrice, stockPriceList[idx+1]['low']))
                print("Drop Rate:%.3f" % (curDropRate *100))
                if stockPriceList[idx+2]['open'] < stockPriceList[idx+1]['close']:
                    print("Next Day Still Drop %.2f (high: %.2f)" % (stockPriceList[idx+2]['open'], stockPriceList[idx+2]['high']))
                    nextDayDrop += 1
                else:
                    None
                    print("Next Day has Raised %.2f" % (stockPriceList[idx+2]['open']))
                print("\n")

    print("Number of day dropped:%d, Number of next day drop:%d" % (numOfDrop, nextDayDrop))

def profitSimulation(stockPriceList, expectDropRate, sellDayLimit):
    NumOfBuyIn = 0
    NumOfSellOut = 0

    for idx, stock in enumerate(stockPriceList):
        preIdx = idx
        curIdx = idx + 1
        if curIdx + 1 > len(stockPriceList):
            break
        
        prePrice = stockPriceList[preIdx]["close"]
        curPrice = stockPriceList[curIdx]["open"]
        
        if curPrice < prePrice:
            curDropRate = (prePrice - curPrice) / prePrice
            if curDropRate >= expectDropRate:
                NumOfBuyIn += 1
                #buyInPrice = (stockPriceList[curIdx]['high'] + stockPriceList[curIdx]['close']) / 2
                buyInPrice = stockPriceList[curIdx]['low']
                print ("[Date:%s] Buy In Stock Price:%.2f" % (stockPriceList[curIdx]['datetime'], buyInPrice), end='')
                maxSellOutPrice = 0;
                for inc in range(1, sellDayLimit+1):
                    if curIdx + inc + 1 > len(stockPriceList) :
                        break
                    if stockPriceList[curIdx + inc]['high'] > maxSellOutPrice:
                        maxSellOutPrice = stockPriceList[curIdx + inc]['high']
                    #if (stockPriceList[curIdx + inc]['high'] - buyInPrice) >= sellPriceLimit:
                    #    NumOfSellOut += 1
                    #    break
                print(" Best Sell Out Price:%.2f Growth:%.3f\n" % (maxSellOutPrice, (maxSellOutPrice-buyInPrice)/buyInPrice))

    print("Number of buy day:%d\n" % (NumOfBuyIn))
                
if __name__ == "__main__":
    #symbol_list = ["INTC", "MSFT", "AMD", "AMZN", "NVDA", "AAPL", "PYPL", "MA", "V", "GOOG", "PA"]
    symbol_list = ["INTC"]
    for symbol in symbol_list:
        print("Company:" + symbol)
        stockPriceList = downloadStockPriceList(symbol)
        #findStockPattern(stockPriceList, 0.005, 10)
        #findStockDropPattern(stockPriceList, 0.005)
        profitSimulation(stockPriceList, 0.008, 30)
    print("Completed!")
