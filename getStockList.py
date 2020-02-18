import requests
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time

apiBaseURL = "https://api.twelvedata.com/"
apiKey = "e763a45b79a14e99983d22e08b10331a"
start_date = '2015-02-10'
end_date = '2020-02-10'

def getStockRange(symbol, sd, ed):
    apiParams = {  \
        'symbol':symbol,\
        'interval':'1day',\
        'apikey':apiKey,\
        'start_date':sd,\
        'end_date':ed\
    }
    apiURL = apiBaseURL + "time_series?"

    resp = requests.get(url=apiURL, params=apiParams);
    stockData = resp.json()
    dateTimeArr = []
    stockCloseArr = []

    if stockData['status'] == 'ok':   
        try:
            for dailyData in stockData['values']:
                dateTimeArr.append(datetime.datetime.strptime(dailyData['datetime'], "%Y-%m-%d"))
                stockCloseArr.append(float(dailyData['close']))

            dateTimeArr.reverse()
            stockCloseArr.reverse()

            return dateTimeArr,stockCloseArr
        except:
            print(stockData['status'])
    
    return None, None
    


def drawStockGraph(symbol):
    dateTimeArr,stockCloseArr = getStockRange(symbol, start_date, end_date)
    
    fig, ax = plt.subplots()
    ax.plot_date(dateTimeArr, stockCloseArr)
    fig.autofmt_xdate()
    ax.set_xlim([datetime.datetime.strptime(start_date, "%Y-%m-%d"), datetime.datetime.strptime(end_date, "%Y-%m-%d")])
    plt.title(symbol + " Stock Trend")
    plt.xlabel("Time")
    plt.ylabel("Stock Price")
    plt.show()

def getStockByMonth(symbol, sd, ed):
    apiParams = {  \
        'symbol':symbol,\
        'interval':'1month',\
        'apikey':apiKey,\
        'start_date':sd,\
        'end_date':ed\
    }
    apiURL = apiBaseURL + "time_series"

    resp = requests.get(url=apiURL, params=apiParams);
    stockData = resp.json()
    dateTimeArr = []
    stockCloseArr = []

    if stockData['status'] == 'ok':
        return float((stockData['values'][0])['close'])
    else:
        return 0.0

def getGrowthRate(symbol):
    start = getStockByMonth(symbol, '2015-01-01', '2015-02-01')
    end = getStockByMonth(symbol, '2020-01-01', '2020-02-01')

    if start == 0.0 or end == 0.0:
        return "failed"
    else:
        return str(start) + " -> " + str(end) +  " = " + str((end-start)/start*100) + "% growth rate"

def main():
    
    df = pd.read_csv("Fortune 500 2017.csv", )
    fortuneList = df['Title'].tolist()
    fortuneStockList = {}
    apiURL = apiBaseURL + "stocks"
    resp = requests.get(apiURL);
    companyList=[]
    if resp.status_code == 200:
        stockData = resp.json()
        for stockData in stockData['data']:
            if stockData['country'] == 'United States':
                foundName = None
                for fCompany in fortuneList:
                    if fCompany in stockData['name']:
                        #print(stockData['name'] +  "=" + stockData['symbol'])
                        fortuneStockList[stockData['name']]= stockData['symbol']
                        foundName = fCompany
                        break
                
                if(foundName != None):
                    fortuneList.remove(foundName)

    timeout = 10
    skipFlag = True
    
    for key, value in fortuneStockList.items():
        if skipFlag:
            if value == 'RS':
                skipFlag = False
            continue
        
        timecount = 0
        while(True):
            timecount += 1
            time.sleep(2)
            msg = getGrowthRate(value)
            if(msg == 'failed'):
                if (timecount == timeout):
                    print(key + "[" + value + "]: " + "Failed to Obtain Data\n")
                    break
                else:
                    continue
            else:
                print(key + "[" + value + "]: " + ": " + msg + "\n")
                break


def getGrowthRateFromList(fortuneStockList):
    timeout = 10
    for key, value in fortuneStockList.items():

        timecount = 0
        while(True):
            timecount += 1
            time.sleep(2)
            msg = getGrowthRate(value)
            if(msg == 'failed'):
                if (timecount == timeout):
                    print(key + "[" + value + "]: " + "Failed to Obtain Data\n")
                    break
                else:
                    continue
            else:
                print(key + "[" + value + "]: " + ": " + msg + "\n")
                break

def recoverStock():
    fortuneStockList = {}
    
    file = open("stock growth rate.txt")
    for line in file:
        if (line == ""):
            continue
        elif ("Failed" in  line):
            tmpStr = line.split("[")
            fortuneStockList[tmpStr[0]] = tmpStr[1].split("]")[0]
        else:
            continue

    #print(fortuneStockList)
    getGrowthRateFromList(fortuneStockList)

def getStockRanking():
    fortuneStockList = {}
    file = open("stock growth rate.txt")

    for line in file:
        if ("growth" in  line):
            tmpStr = line.split("[")
            name = tmpStr[0]
            tmpStr = tmpStr[1].split("]")
            symbol = tmpStr[0]
            tmpStr = tmpStr[1].split("=")
            curPrice = tmpStr[0].split("->")[1]
            growth = float((tmpStr[1])[1:4])
            fortuneStockList[name + "(" + symbol + " - " + curPrice + ")" ] = growth

    sortedDict = {k: v for k, v in sorted(fortuneStockList.items(), key=lambda item: item[1])}
    for key, val in sortedDict.items():
        print(key + ":" + str(val))

if __name__ == "__main__":
    #main()
    #recoverStock()
    getStockRanking()
    #...
    print("Task Completed!!!")






