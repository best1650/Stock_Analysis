import requests
import os
import time

sleepTime = 2
stockFilePath = "cleanStockList.csv"
apiBaseURL = "https://api.twelvedata.com/"
apiKey = "e763a45b79a14e99983d22e08b10331a"
start_date = '2016-02-20'
end_date = '2020-02-20'
interval = '1day'

def writeStockData(symbol):
    print(symbol + " Downloading....", end = '')
    
    retVal = False
    
    directory = 'stockData/' + symbol
    if not os.path.exists(directory):
        os.makedirs(directory)
    file = open(directory + '/price.txt', 'w')
    
    apiParams = {  \
        'symbol':symbol,\
        'interval':interval,\
        'apikey':apiKey,\
        'start_date':start_date,\
        'end_date':end_date\
    }
    apiURL = apiBaseURL + "time_series?"

    resp = requests.get(url=apiURL, params=apiParams);
    stockData = resp.json()  

    if stockData['status'] == 'ok':
        for dailyData in stockData['values']:
            file.write(dailyData['datetime']+","+dailyData['close']+","+dailyData['volume']+"\n")
        retVal = True
        
    file.close()
    if retVal:
        print("Completed!")
    else:
        print("Failed!")
    return retVal
    

def downloadStock():
    file = open(stockFilePath, 'r')

    isHeader = True
    for line in file:
        if isHeader:
            isHeader = False
        else:
            numOfRetry = 2
            time.sleep(sleepTime)
            while( not writeStockData(line.split(',')[1]) and numOfRetry > 0):
                numOfRetry -= 1
                time.sleep(10)

    file.close()
    
if __name__ == "__main__":
    downloadStock()



    
