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
STOCK_START_DATE = '2020-02-28'
STOCK_END_DATE = '2020-02-29'
STOCK_INTERVAL = '1min'
#TIME_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def parseDate(dateTime):
    return datetime.datetime.strptime(dateTime, TIME_FORMAT)

def downloadStockDataList(symbol):
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

    stockDataList = {}
    stockDataList['datetime'] = []
    stockDataList['open'] = []
    stockDataList['high'] = []
    stockDataList['low'] = []
    stockDataList['close'] = []
    stockDataList['inc'] = []
    stockDataList['dec'] = []
    
    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            stockDataList['datetime'].insert(0, parseDate(dailyData['datetime']))
            stockDataList['open'].insert(0, float(dailyData['open']))
            stockDataList['high'].insert(0, float(dailyData['high']))
            stockDataList['low'].insert(0, float(dailyData['low']))
            stockDataList['close'].insert(0, float(dailyData['close']))
            tmpInc = ( float(dailyData['high']) - float(dailyData['open']) ) / float(dailyData['open'])
            tmpDec = ( float(dailyData['open']) - float(dailyData['low']) ) / float(dailyData['open'])
            stockDataList['inc'].insert(0, tmpInc)
            stockDataList['dec'].insert(0, tmpDec)

    return stockDataList

def getStockPricePrediction(stockPrice, diffRate):
    #incRate = 1.00 + (np.average(incList) /5.0)
    incRate = 1.00
    #decRate = 1.00 - np.average(decList)
    decRate = 1.00 - diffRate
    buyInPrice = stockPrice * decRate
    sellOutPrice = stockPrice * incRate 
    return buyInPrice, sellOutPrice, incRate, decRate

def training(stockDataList, investment, diffRate):
    totalProfit = 0.0

    dayIdx = 0
    #startIdx = 0
    #endIdx = startIdx + interval
    numOfDay = len(stockDataList['inc'])
    numOfDayBuyIn = 0
    numOfDaySellOut = 0
    numOfDayNotBuy = 0

    while dayIdx != numOfDay:
        openStockPrice = stockDataList['open'][dayIdx]
        lowStockPrice = stockDataList['low'][dayIdx]
        highStockPrice = stockDataList['high'][dayIdx]

        buyInPrice, sellOutPrice, incRate, decRate = getStockPricePrediction(openStockPrice,diffRate)

        numOfShare = investment / buyInPrice
        
        if (buyInPrice >= lowStockPrice) and (buyInPrice <= highStockPrice):
            numOfDayBuyIn += 1
            #print ('[Y-', end='')
            if sellOutPrice <= highStockPrice:
                numOfDaySellOut += 1
                #print ('Y] ', end='')
                dailyEarning = (sellOutPrice - buyInPrice) * numOfShare
                totalProfit += dailyEarning
                #print(dailyEarning)
                #print("Buy in price:%.2f (%.4f), Sell out price:%.2f (%.4f), Earned per share: %.2f, Daily low price:%.2f, Daily high price:%.2f\n"\
                #      % (buyInPrice, decRate, sellOutPrice, (sellOutPrice - buyInPrice), incRate, lowStockPrice, highStockPrice) )
            else:
                None
                #print ('N] ', end='')
                #print("Buy in price:%.2f (%.4f), Sell out price:%.2f (%.4f), Money earned per-share:%.2f"+\
                #      "Daily low price:%.2f, Daily high price:%.2f\n"\
                #  % (buyInPrice, decRate, sellOutPrice, incRate, float(sellOutPrice - buyInPrice), lowStockPrice, highStockPrice) )
        else:
            numOfDayNotBuy += 1
            #print ('[N-N] ', end='')

        #print("Buy in price:%.2f (%.4f), Sell out price:%.2f (%.4f), Daily low price:%.2f, Daily high price:%.2f\n"\
        #      % (buyInPrice, decRate, sellOutPrice, incRate, lowStockPrice, highStockPrice) )

        dayIdx += 1
        #endIdx += 1


    #print( "Diff Rate:%.4f, Num of buy in day:%d (sell out: %d), Num of not buy day:%d, Total Revenue: %.2f\n"\
    #       % (diffRate, numOfDayBuyIn, numOfDaySellOut, numOfDayNotBuy, totalProfit) )

    return totalProfit, numOfDayBuyIn

def drawGraph(x, y):
    fig, ax = plt.subplots()
    ax.plot(x, y, 'g-')
    plt.show()

def startSimulation(symbol):
    stockDataList = downloadStockDataList(symbol)
    numOfTotalDay = float(len(stockDataList['datetime']))
    priceDiffList = []
    profitList = []
    numOfDayBuyInList = []

    bestProfit = 0.0
    bestPriceDiff = 0.0
    bestNumOfDayBuyIn = 0
    
    priceDiff = 0.001
    priceLimit = 0.1
    while priceDiff <= priceLimit:
        priceDiffList.append(priceDiff)
        totalProfit, numOfDayBuyIn = training(stockDataList, 2000, priceDiff)
        profitList.append(totalProfit)
        numOfDayBuyInList.append(numOfDayBuyIn)

        if totalProfit >= bestProfit:
            bestProfit = totalProfit
            bestPriceDiff = priceDiff
            bestNumOfDayBuyIn = numOfDayBuyIn
        
        priceDiff += 0.001

    print ("bestProfit: %.2f (per day:%.2f), bestPriceDiff:%.3f, bestNumOfDayBuyIn:%d" % (bestProfit, (bestProfit / numOfTotalDay), bestPriceDiff, bestNumOfDayBuyIn))
    #drawGraph(priceDiffList, profitList)

def dayTradePrice(stockPriceList, buyInRatio, sellOutRatio):
    avgPrice = np.average(stockPriceList)
    buyInPrice = avgPrice * buyInRatio
    sellOutPrice = avgPrice * sellOutRatio
    #print("Buy in price:%.2f, Sell out price:%.2f" % (buyInPrice, sellOutPrice))
    return buyInPrice, sellOutPrice

def getDayTradeResult(stockPriceList, buyInPrice, sellOutPrice):
    isBuy = False
    isSell = False

    for curPrice in stockPriceList:
        if not isBuy:
            if curPrice <= buyInPrice:
                isBuy = True
        else:
            if not isSell:
                if curPrice >= sellOutPrice:
                    isSell = True
                    break

    return isBuy, isSell
            

def dayTradeTraining(stockDataList, stockPriceLen):
    #stockDataList = downloadStockDataList("AMD")
    #stockPriceLen = len(stockDataList['datetime'])
    midPt = stockPriceLen // 2

    buyInPrice, sellOutPrice = dayTradePrice(stockDataList[:midPt], 0.98, 0.99)
    isBuy, isSell = getDayTradeResult(stockDataList[midPt:], buyInPrice, sellOutPrice)

    print("Buy In:%s (%.2f), Sell out:%s (%.2f)" % (str(isBuy), buyInPrice, str(isSell), sellOutPrice))

if __name__ == "__main__":
    #dayTradeTraining()

    file = open("dailyStockPrice/AMD.txt", 'r')

    for line in file:
        strList = line.split(',')
        strList = strList[:len(strList)-2]
        stockDataList = []
        for term in strList:
            if term != "":
                stockDataList.append(float(term))
        
        stockPriceLen = len(stockDataList)
        dayTradeTraining(stockDataList, stockPriceLen)
        
    file.close()
    
    print("Completed!")















    
