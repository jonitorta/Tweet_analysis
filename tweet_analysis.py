#Useful libraries we need.
from datetime import date, datetime
from unicodedata import name
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
#nltk.download('stopwords')


extra_stop_words = ["no","si","así","hacer","cosas","ver","voy","va","puedes","luego",
                    "ser","hecho","hace","tener","sé","mejor","dicho"]
stopWords = stopwords.words("spanish") + extra_stop_words

#Select twitter querry we want to obtain tweets.
querry = "(from:@titodeskanar)"
#If enough tweets are found program will collect at max limit number.
limit = 50





#Here we define an object to make easy analyse multiple users or querrys.
class Tweet_analysis() : 
    #We ask for the querre and tweet limit
    def __init__(self, querry, limit = 500,user_info = False):
        self.querry = querry
        #We create a list for the tweet object
        tweets = []
        #Here we get the tweet objects and append them to the list
        for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
            if len (tweets) == limit : break
            #Here we collect the date, user and content from the tweet
            else : tweets.append([ tweet.date, tweet.user.username , tweet.content,
                                tweet.replyCount, tweet.retweetCount, tweet.likeCount, tweet.quoteCount ])
            #If user info is true three extra attributes are created
            #1) unique_user_name is a list of unique user names in the querry
            #2)user info is a list, every instance of the list containt general info about each unique user
            #3) user info attributes is a list of attributes we can call for each user_info like description or followersCount
        if user_info :
            unique_user_name = set( [t[1] for t in tweets] )
            self.unique_user_name =  [name for name in unique_user_name  ]
            self.user_info = [sntwitter.TwitterUserScraper(username=name)._get_entity() for name in self.unique_user_name]
            self.user_info_attributes = ["username", "id", "displayname", "description",
			"rawDescription", "descriptionUrls", "created", "followersCount", "friendsCount", 
			"statusesCount", "favouritesCount", "listedCount", "mediaCount","location",
			"protected", "linkUrl","linkTcourl", "profileImageUrl", 
			"profileBannerUrl", "label"]
        df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet","Reply count","Retweet count","Like count","Quote count"] )
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
    
    def averague_tweets(self,n_days = 30, round_number = 3):
        tweets = 0
        for i in self.tweets_per_day(n_days) : 
            tweets +=i
        return round(tweets/n_days,round_number)








#tweets = []
#Here we get the tweet objects and append them to the list
#for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
#    if len (tweets) == limit : break
#Here we collect the date, user and content from the tweet
#    else : tweets.append([ tweet.date, tweet.user , tweet.content ])
#df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
#df["Date"] = [date(d.year , d.month , d.day ) for d in df["Date"]]
#print( df["Date"] )
User = Tweet_analysis(querry,user_info=True).geneal_info
print(User)
















pass