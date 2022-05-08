#Useful libraries we need.
from copy import copy
from datetime import date, datetime
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter

#Select twitter querry we want to obtain tweets.
querry = "(from:@EvilAFM)"
#If enough tweets are found program will collect at max limit number.
limit = 50





#Here we define an object to make easy analyse multiple users or querrys.
class Tweet_analysis() : 
    #We ask for the querre and tweet limit
    def __init__(self, querry, limit = 500):
        self.querry = querry
        #We create a list for the tweet object
        tweets = []
        #Here we get the tweet objects and append them to the list
        for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
            if len (tweets) == limit : break
            #Here we collect the date, user and content from the tweet
            else : tweets.append([ tweet.date, tweet.user , tweet.content ])
        df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
        self.content = df["Tweet"]
        self.dates = df["Date"]
        self.info = df["User"]
        self.geneal_info = df
    
    
    #Method to obtain # of most common words from the tweets of the querry, len_filter
    #filter the words with less or equal number of letters.
    def common_words(self, number = 10, len_filter = 3):
        tweet_longer = ""
        for t in self.content:
            tweet_longer +=t 
        count = Counter(tweet_longer.split(" "))
        lista, diccionario = list(count) , dict(count) 
        index_short_element = np.where( (np.array ([len(element) for element in lista] ) )<=len_filter )[0]
        for index in index_short_element :
            diccionario.pop( lista[index] )
        count = Counter(diccionario).most_common(number)
        return dict(count)

#Count tweets per day
    def tweets_per_day(self,last_n_days = 30) :
        copy_df = self.geneal_info
        copy_df["Date"] = [fechas.to_pydatetime().date() for fechas in self.geneal_info["Date"]]
        tweets_per_day = copy_df.groupby("Date").count()["Tweet"]
        return tweets_per_day[0:last_n_days]




#tweets = []
#for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
#    if len (tweets) == limit : break
#    else : tweets.append([ tweet.date, tweet.user , tweet.content ])
#df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )

#copy_df = df
#copy_df["Date"] = [fechas.to_pydatetime().date() for fechas in df["Date"]]
#tweets_per_day = copy_df.groupby("Date").count()["Tweet"]
#print(tweets_per_day[0:30])

#Dates = [fechas.to_pydatetime().date() for fechas in df["Date"]]
#copy_df["Date"] = Dates







User = Tweet_analysis(querry=querry)
print(User.tweets_per_day())


pass