import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter

querry = "(from:@EvilAFM)"
tweets = [] 
limit = 50

for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
    if len (tweets) == limit : break
    else : tweets.append([ tweet.date, tweet.user , tweet.content ])

df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
#print(df)

tweet_longer = ""
for t in df["Tweet"]:
    tweet_longer +=t 

count = Counter(tweet_longer.split(" "))
short_words_index = np.where( np.array( [ len(text) for text in list(count) ] ) <= 3)























class Tweet_analysis() : 
    
    def __init__(self,content,dates,info):
        self.content = content
        self.dates = dates
        self.info = info

    def commond_words(self,number = 10):
        tweet_longer = ""
        for t in self.content:
            tweet_longer +=t 
        count = Counter(tweet_longer.split(" "))
        return count.most_common(number)


pass