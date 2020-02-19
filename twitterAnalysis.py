import twitter

twAPI = twitter.Api( \
    consumer_key='jKgmYutVntIe3lnbEWUGqVOnK',\
    consumer_secret='kyyzK7hiufNShyaZBzQgNcvrtVogZ4O8yfQ8RJfa3LHjRjFWt6',\
    access_token_key='1229875341264551936-7ZFL4cIxxC1zdWmpAWfBeMhnGYW1HP',\
    access_token_secret='L3ZQtmp8wPWNwWZ5AuptC2wIjvCWjjhfW14RGCslkv3fm'\
)
statuses = twAPI.GetUserTimeline("88943677")
#API2 = twitter.Api()
#statuses = API2.GetUserTimeline("88943677")
#twAPI.VerifyCredentials()
#if __name__ == "__main__":
    #print(twAPI.VerifyCredentials())
