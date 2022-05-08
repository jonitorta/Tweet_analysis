from xml.dom.minidom import Element
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter

querry = "(from:@elonmusk)"
tweets = [] 
limit = 500

for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
    if len (tweets) == limit : break
    else : tweets.append([ tweet.date, tweet.user , tweet.content ])

df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
#print(df)

tweet_longer = ""
for t in df["Tweet"]:
    tweet_longer +=t 

count = Counter(tweet_longer.split(" "))
lista, diccionario = list(count) , dict(count) 
index_short_element = np.where( (np.array ([len(element) for element in lista] ) )<=3 )[0]
for index in index_short_element :
    diccionario.pop( lista[index] )
count = Counter(diccionario).most_common(int(limit/10))






















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