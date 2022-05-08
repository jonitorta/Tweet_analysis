from xml.dom.minidom import Element
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
from collections import Counter

querry = "(from:@titodeskanar)"
limit = 500
class Tweet_analysis() : 
    
    def __init__(self,querry,limit = 500):
        self.querry = querry
        tweets = []
        for tweet in sntwitter.TwitterSearchScraper(querry).get_items():
            if len (tweets) == limit : break
            else : tweets.append([ tweet.date, tweet.user , tweet.content ])
        df = pd.DataFrame( tweets, columns=["Date", "User", "Tweet"] )
        self.content = df["Tweet"]
        self.dates = df["Date"]
        self.info = df["User"]
        self.geneal_info = df
    
    
    
    def commond_words(self,number = 10, len_filter = 3):
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

User = Tweet_analysis(querry=querry)
commond = User.commond_words()

pass