#Useful libraries we need.
from datetime import date, datetime
from winreg import QueryReflectionKey
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from config_file import options

#nltk.download('stopwords')


extra_stop_words = options["extra stop words spanish"]
idiom = options["idiom"]
stopWords = stopwords.words(idiom) + extra_stop_words







#Here we define an object to make easy analyse multiple users or querrys.
class Tweet_analysis() : 
    #We ask for the querry and tweet limit
    def __init__(self,querry,limit = 500, save_data=False , file_name="saved_data.pkl" ):
        self.querry = querry
        self.limit = limit
        self.save_status = save_data
        self.file_name = file_name
        

    def get_tweets(self):
        #We create a list for the tweet object
        tweets = []
        #Here we get the tweet objects and append them to the list
        for tweet in sntwitter.TwitterSearchScraper(self.querry).get_items():
            if len (tweets) == self.limit : break
            #Here we collect the date, user and content from the tweet
            else : 
                try:
                    user_info = sntwitter.TwitterUserScraper(username=tweet.user.username)._get_entity()
                except KeyError : 
                    user_info = None
                
                if user_info is None :    
                    tweets.append([ tweet.date, tweet.user.username , tweet.content,
                                tweet.replyCount, tweet.retweetCount, tweet.likeCount, tweet.quoteCount,
                                None, None, None, None   ])
                else :
                    tweets.append([ tweet.date, tweet.user.username , tweet.content,
                                tweet.replyCount, tweet.retweetCount, tweet.likeCount, tweet.quoteCount,
                                user_info.followersCount, user_info.friendsCount, user_info.created, user_info.mediaCount   ])
                
                df = pd.DataFrame( tweets, columns=[ "Date", "User", "Tweet","Reply count","Retweet count",
                                             "Like count","Quote count","Account followers","Account friends",
                                             "Account creation", "Account media"       ])
        df["Date"] = [ date(d.year , d.month , d.day ) for d in df["Date"] ]
        self.content = df["Tweet"]
        self.dates = df["Date"]
        self.info = df["User"]
        self.geneal_info = df
        self.tweets_per_username = self.geneal_info.groupby("User").count()["Tweet"]
        self.called = True
        if self.save_status : 
            self.geneal_info.to_pickle(self.file_name)
        
    
    
    #Method to obtain # of most common words from the tweets of the querry, len_filter
    #filter the words with less or equal number of letters.
    def common_words(self, number = 10):
        if self.called :
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
        else : print("No tweets appended call get tweets first.")

#Count tweets per day
    def tweets_per_interval_of_time(self, last_n_days = 30 ) :
        copy_df = self.geneal_info
        tweets_per_day = copy_df.groupby("Date").count()["Tweet"]
        return tweets_per_day[-1-last_n_days : -1]
    
    def averague_tweets(self,n_days = 30, round_number = 3):
        tweets = 0
        for i in self.tweets_per_interval_of_time(n_days) : 
            tweets +=i
        return round(tweets/n_days,round_number)


    
















