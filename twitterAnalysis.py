import twitter
import pprint
import json

twAPI = twitter.Api( \
    consumer_key='jKgmYutVntIe3lnbEWUGqVOnK',\
    consumer_secret='kyyzK7hiufNShyaZBzQgNcvrtVogZ4O8yfQ8RJfa3LHjRjFWt6',\
    access_token_key='1229875341264551936-7ZFL4cIxxC1zdWmpAWfBeMhnGYW1HP',\
    access_token_secret='L3ZQtmp8wPWNwWZ5AuptC2wIjvCWjjhfW14RGCslkv3fm'\
)

def buildTestSet(search_keyword):
    try:
        tweets_fetched = twAPI.GetSearch(search_keyword, count = 100)
        
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)
        
        return [{"text":status.text, "label":None} for status in tweets_fetched]
    except:
        print("Unfortunately, something went wrong..")
        return None

def buildTrainingSet(corpusFile, tweetDataFile):
    import csv
    import time
    
    corpus = []
    
    with open(corpusFile, 'r') as csvfile:
        lineReader = csv.reader(csvfile,delimiter=',', quotechar="\"")
        for row in lineReader:
            corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})
            
    rate_limit = 180
    sleep_time = 900/180
    
    trainingDataSet = []
    
    for tweet in corpus:
        try:
            status = twAPI.GetStatus(tweet["tweet_id"])
            print("Tweet fetched" + status.text)
            tweet["text"] = status.text
            trainingDataSet.append(tweet)
            time.sleep(sleep_time)
        except: 
            continue
        
    # now we write them to the empty CSV file
    with open(tweetDataFile,'w') as csvfile:
        linewriter = csv.writer(csvfile,delimiter=',',quotechar="\"")
        for tweet in trainingDataSet:
            try:
                linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
            except Exception as e:
                print(e)
    return trainingDataSet

if __name__ == "__main__":
    corpusFile = "corpus.csv"
    tweetDataFile = "tweetDataFile.csv"

    trainingData = buildTrainingSet(corpusFile, tweetDataFile)
    print("Completed!!")
