import os
import operator

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

if __name__ == "__main__":
    initStockList()

    while True:
        userInput = input("Stock@:")
        userInput = userInput.lower().split(" ")
        if (userInput[0] == "exit"):
            break
        elif (userInput[0] == "rank"):
            printStockGrowthRateRanking(int(userInput[1]))
        elif (userInput[0] == "re"):
            recommendedStockList(int(userInput[1]))  
        elif (userInput[0] == "stock"):
            symbole = userInput[1].upper()
            stockPriceList = getStockPriceList(symbole)
            if len(stockPriceList) != 0:
                runStockCalculation(symbole, stockPriceList)









