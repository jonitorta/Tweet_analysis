#Useful libraries we need.
from datetime import date
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import download
#download('stopwords')


extra_stop_words = ["no","si","así","hacer","cosas","ver","voy","va","puedes","luego",
                    "ser","hecho","hace","tener","sé","mejor","dicho"]
stopWords = stopwords.words("spanish") + extra_stop_words

#Select twitter querry we want to obtain tweets
querry = "(from:@titodeskanar)"
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
    def common_words(self, number = 10):
        tweet_longer = ""
        f_tweet_longer = []
        for t in self.geneal_info["Tweet"]: tweet_longer +=t
        tweet_longer = tweet_longer.lower()
        count = Counter(tweet_longer.split(" "))
        lista, diccionario = list(count) , dict(count) 
        for w in lista :
            if w not in stopWords :
                f_tweet_longer.append(w)
        times_word_appear = [diccionario[j] for j in f_tweet_longer]
        common_words = Counter(dict(zip(f_tweet_longer,times_word_appear  ))).most_common(number)
        return common_words

#Count tweets per day
    def tweets_per_day(self, last_n_days = 30 ) :
        copy_df = self.geneal_info
        copy_df["Date"] = [ date(d.year , d.month , d.day ) for d in copy_df["Date"] ]
        tweets_per_day = copy_df.groupby("Date").count()["Tweet"]
        return tweets_per_day[-1-last_n_days : -1]








#tweets = []
#Here we get the tweet objects and append them to the list
#for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
#    if len (tweets) == limit : break
#Here we collect the date, user and content from the tweet
#    else : tweets.append([ tweet.date, tweet.user , tweet.content ])
#df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
#df["Date"] = [date(d.year , d.month , d.day ) for d in df["Date"]]
#print( df["Date"] )
User = Tweet_analysis(querry)
info = User.geneal_info
print(User.tweets_per_day())














pass