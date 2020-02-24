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

warnings.filterwarnings("ignore")

MIN_COUNT = 500
ONE_MONTH = 22
THREE_MONTH = ONE_MONTH * 3
HALF_YEAR = ONE_MONTH * 6
ONE_YEAR = ONE_MONTH * 12
TWO_YEAR = ONE_YEAR * 2
THREE_YEAR = ONE_YEAR * 3
FOUR_YEAR = ONE_YEAR * 4
BORDER_LEN = 70
global STOCK_PRICE_LIST

STOCK_API_URL = "https://api.twelvedata.com/"
STOCK_API_KEY = "e763a45b79a14e99983d22e08b10331a"
STOCK_START_DATE = '2019-08-24'
STOCK_END_DATE = '2020-02-24'
STOCK_INTERVAL = '1day'

def getStockPriceList(symbol, adjustment=ONE_YEAR):
    stockPath = "stockData/" + symbol + "/price.txt"
    stockFile = open(stockPath, 'r')
    stockPriceList = []
    lineCount = 0
    for dailyStockData in stockFile:
        lineCount += 1
        stockPriceList.append(float(dailyStockData.split(",")[1]))
    stockFile.close()

    if lineCount < MIN_COUNT:
        #print(symbol + ": Stock Data is Missing!")
        stockPriceList = []
  
    return stockPriceList[0:adjustment] 

def printBorder(title=""):
    if(len(title) == 0):
        print("*" * BORDER_LEN)
    else:
        starLen = BORDER_LEN - len(title)
        leftStarLen = starLen // 2
        rightStartLen = starLen - leftStarLen
        leftStarLen -= 1
        rightStartLen -= 1
        print(("*" * leftStarLen) + " " + title + " " + ("*" * rightStartLen))

def getStockProbability(division, stockPriceList):
    totalDay = float(len(stockPriceList))
    stockMax = max(stockPriceList)
    stockLow = min(stockPriceList)
    divisionRange = (stockMax - stockLow) / division
    pList = [0] * division
    for price in stockPriceList:
        rank = int((price - stockLow) / divisionRange)
        if (rank >= division):
            rank = division - 1
        pList[rank] += 1

    for i in range(1, division+1):
        classP = round((float(pList[i-1]) / totalDay * 100), 3)
        classStr = "Class " + str(i) + ":" + str(classP) + "%" 
        classStr += "\tPrice Range:"
        classMin = round((stockLow + divisionRange * (i-1)), 2)
        classMax = round((stockLow + divisionRange * (i)), 2)
        classStr += str(classMin) + "~" + str(classMax)
        print(classStr)

def getStockGrowthRate(stockPriceList):
    startPrice = stockPriceList[-1]
    endPrince = stockPriceList[0]
    growthRate = round(((endPrince - startPrice) / startPrice * 100), 2) 
    return growthRate

def runStockCalculation(symbol, stockPriceList):
    printBorder( symbol + " Stock Status " )
    growthRate = getStockGrowthRate(stockPriceList) 

    lowestPriceStat = "\n" +\
        "Current Price:" + str(stockPriceList[0]) +"\n"+\
        "LP in One Month:" + str(min(stockPriceList[0:ONE_MONTH])) +"\n"+\
        "LP in Three Month:" + str(min(stockPriceList[0:THREE_MONTH])) +"\n"+\
        "LP in Half Year:" + str(min(stockPriceList[0:HALF_YEAR])) +"\n"+\
        "LP in One Year:" + str(min(stockPriceList[0:ONE_YEAR])) +"\n"+\
        "Stock LP:" +  str(min(stockPriceList)) +"\n"+\
        "Stock HP:" +  str(max(stockPriceList)) +"\n"+\
        "Growth Rate:" + str(growthRate) +"%\n"
 
    print(lowestPriceStat)
    getStockProbability(7, stockPriceList)
    printBorder()

def getStockGrowthRateRanking(adjustment=ONE_YEAR):
    stockListFile = open("cleanStockList.csv", "r")
    isHeader = True 
    stockGrowthList = {}
    for stockData in stockListFile:
        if isHeader:
            isHeader = False
        else:
            stockDataTokens = stockData.split(",")
            stockName = stockDataTokens[0]
            stockSymbol = stockDataTokens[1]
            stockPriceList = getStockPriceList(stockSymbol, adjustment)
            if len(stockPriceList) != 0:
                stockKey = stockName + " (" + stockSymbol + ")"
                stockGrowthList[stockKey] = getStockGrowthRate(stockPriceList)
    
    sortedStockGrowthList = \
    {k:v for k, v in \
    sorted(stockGrowthList.items(), key=lambda item:item[1], reverse=True)}

    return sortedStockGrowthList

def printStockGrowthRateRanking(displayLimit):
    global STOCK_PRICE_LIST
    sortedStockGrowthList = getStockGrowthRateRanking() 
    printBorder("Ranking")
    counter = 0
    for key, val in sortedStockGrowthList.items():
        counter+=1
        print(str(counter) + ".\t" + key + ":" + str(val) + "%" +\
              " - $" + STOCK_PRICE_LIST[key])
        if counter >= displayLimit:
            break

    printBorder()        

def intersection(list1, list2):
    return list(set(list1) & set(list2))

def getTopStockList(sortedStockGrowthList, topRank):
    topStockList = []
    counter = 0
    for key, val in sortedStockGrowthList.items():
        counter+=1
        topStockList.append(key)
        if counter >= topRank:
            break
    return topStockList

def recommendedStockList(topRank=100):
    global STOCK_PRICE_LIST
    
    timeRangeList = [ONE_MONTH, THREE_MONTH, HALF_YEAR, ONE_YEAR, TWO_YEAR, THREE_YEAR, FOUR_YEAR]
    stockInTimeRange = []
    for timeRange in timeRangeList:
        sortedStockGrowthList = getStockGrowthRateRanking(timeRange)
        stockInTimeRange.append(getTopStockList(sortedStockGrowthList, topRank))
    
    rtnList = stockInTimeRange[0]
    for idx in range(1, len(timeRangeList)):
        list1 = rtnList
        list2 = stockInTimeRange[idx]
        rtnList = intersection(list1, list2)

    counter = 0
    printBorder("Recommendation")
    for stock in rtnList:
        counter += 1
        print(str(counter) + "\t" + stock +\
              " - $" + STOCK_PRICE_LIST[stock])
    printBorder()

def initStockList():
    global STOCK_PRICE_LIST
    STOCK_PRICE_LIST = {}
    stockListFile = open("cleanStockList.csv", "r")
    isHeader = True 
    stockGrowthList = {}
    for stockData in stockListFile:
        if isHeader:
            isHeader = False
        else:
            stockDataTokens = stockData.split(",")
            stockName = stockDataTokens[0]
            stockSymbol = stockDataTokens[1]
            stockPrice = stockDataTokens[2]
            stockKey = stockName + " (" + stockSymbol + ")"
            STOCK_PRICE_LIST[stockKey] = stockPrice

def searchCompanyInWiki(key):
    printBorder("Search Result")
    wikiBaseURL = "https://en.wikipedia.org/w/api.php?"
    apiParams = {  \
        'action':'query',\
        'format':'json',\
        'list':'search',\
        'srsearch':urllib.parse.quote(key)
    }
    
    resp = requests.get(url=wikiBaseURL, params=apiParams, verify=False);
    searchJson = json.loads(resp.content)
    #searchJson = resp.json() 
    searchResultList = searchJson['query']['search']
    if len(searchResultList) == 0:
        print("")
    else:
        for searchItem in searchResultList:
            print(searchItem['title'] + " (" + str(searchItem['pageid']) + ")")
            
    printBorder()

def printWikiText(wikiText):
    print()
    indentText = " " * 3
    wikiTextList = wikiText.split("\n")
    for wikiTextToken in wikiTextList:
        wrapper = textwrap.TextWrapper(\
            width=65,\
            initial_indent=indentText,\
            subsequent_indent=indentText\
        ) 
        word_list = wrapper.wrap(text=wikiTextToken) 
        printText = ""
        for element in word_list: 
            printText += element + "\n"

        print(printText)
        
def getWikiData(pageId):
    wikiBaseURL = "https://en.wikipedia.org/w/api.php?"
    apiParam = "action=query&format=json&prop=extracts&exintro&explaintext&pageids="
    
    resp = requests.get(url=wikiBaseURL+apiParam+str(pageId), verify=False);
    searchJson = json.loads(resp.content)
    #searchJson = resp.json()  
    wikiData = searchJson['query']['pages'][str(pageId)]
    wikiTitle = wikiData['title']
    wikiText = wikiData['extract']
    
    printBorder(wikiTitle)
    printWikiText(wikiText)
    printBorder()

def parseDate(dateTime):
    return datetime.datetime.strptime(dateTime, "%Y-%m-%d")

def getStockPrice(symbol):
    apiParams = {  \
        'symbol':symbol,\
        'interval':STOCK_INTERVAL,\
        'apikey':STOCK_API_KEY,\
        'start_date':STOCK_START_DATE,\
        'end_date':STOCK_END_DATE\
    }
    
    apiURL = STOCK_API_URL + "time_series?"

    resp = requests.get(url=apiURL, params=apiParams, verify=False);
    stockData = json.loads(resp.content)
    #stockData = resp.json()  

    dateTimeList = []
    dailyPriceList = []
    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            dateTimeList.append( parseDate(dailyData['datetime']) )
            dailyPriceList.append( float(dailyData['close']) )

    dateTimeList.reverse()
    dailyPriceList.reverse()
    return dateTimeList, dailyPriceList

def getStockEma(symbol, interval):
    apiParams = {  \
        'symbol':symbol,\
        'interval':STOCK_INTERVAL,\
        'apikey':STOCK_API_KEY,\
        'start_date':STOCK_START_DATE,\
        'end_date':STOCK_END_DATE,\
        'time_period':interval
    }

    apiURL = STOCK_API_URL + "ema"

    resp = requests.get(url=apiURL, params=apiParams, verify=False);
    stockData = json.loads(resp.content)
    #stockData = resp.json()  

    dailyEmaList = []

    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            dailyEmaList.append(float(dailyData['ema']))

    dailyEmaList.reverse()
    return dailyEmaList
 
def drawStockGraph(symbol):
    dateTimeList, dailyPriceList = getStockPrice(symbol)
    time.sleep(0.5)
    dailyEma5List = getStockEma(symbol, 5)
    time.sleep(0.5) 
    dailyEma10List = getStockEma(symbol, 10)
    time.sleep(0.5)
    dailyEma20List = getStockEma(symbol, 20)
    
    dateTimeNP = np.array(dateTimeList)
    dailyPriceNP = np.array(dailyPriceList)
    dailyEma5NP = np.array(dailyEma5List)
    dailyEma10NP = np.array(dailyEma10List)
    dailyEma20NP = np.array(dailyEma20List)
    
    fig, ax = plt.subplots()
    ax.plot_date(dateTimeNP, dailyPriceNP,'y-', label='Daily Stock Price')
    ax.plot_date(dateTimeNP, dailyEma5NP,'r-', label='Daily Stock EMA (5)')
    ax.plot_date(dateTimeNP, dailyEma10NP,'g-', label='Daily Stock EMA (10)')
    ax.plot_date(dateTimeNP, dailyEma20NP,'b-', label='Daily Stock EMA (20)')

    ax.legend(loc='upper center', shadow=True, fontsize='small')
    fmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(fmt)
    fmt = mplcursors.cursor(hover=True)
    fig.autofmt_xdate()
    
    fig.set_size_inches(15,8)
    plt.title(symbol + " Stock Trend", fontsize=24)
    plt.xlabel("Time", fontsize=18)
    plt.ylabel("Stock Price", fontsize=18)

    #idx = np.argwhere(\
    #    np.diff(np.sign(dailyPriceNP - dailyEmaNP))).flatten()
    #plt.plot(dateTimeNP[idx], dailyPriceNP[idx], 'go')
    plt.show()

if __name__ == "__main__":
    initStockList()
    while True:
        userInput = input("Stock@:")
        userInput = userInput.lower().split(" ")
        if (userInput[0] == "exit"):
            break
        elif (userInput[0] == "search"):
            searchCompanyInWiki(userInput[1])
        elif (userInput[0] == "wiki"):
            getWikiData(int(userInput[1]))
        elif (userInput[0] == "rank"):
            printStockGrowthRateRanking(int(userInput[1]))
        elif (userInput[0] == "re"):
            recommendedStockList(int(userInput[1]))
        elif (userInput[0] == "graph"):
            drawStockGraph(userInput[1])
        elif (userInput[0] == "stock"):
            symbole = userInput[1].upper()
            stockPriceList = getStockPriceList(symbole)
            if len(stockPriceList) != 0:
                runStockCalculation(symbole, stockPriceList)
                









