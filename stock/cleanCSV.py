cleanFile = open("cleanStockList.csv", "w")
f = open("companyList.csv", "r", encoding='ISO-8859-1')
header = True
for stock in f:
    stockData = stock.split(",")
    if header:
        cleanFile.write(  stockData[1] + "," +\
                          stockData[2] + "," +\
                          stockData[4][3:] + "," +\
                          "Dividend\n")
        header = False
    else:
        cleanFile.write(  stockData[1] + "," +\
                          stockData[2] + "," +\
                          stockData[4][3:] + "," +\
                          "0\n")    
f.close()
cleanFile.close()
