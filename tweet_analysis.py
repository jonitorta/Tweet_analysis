import pandas as pd
import numpy as np
from tweet_scrapper import Tweet_analysis
from config_file import options
from os import path


querry = options["querry"]
limit = options["limit"]
save_status = options["save status"]
file_name = options["file name"]
commond_words_file = options["commond_word_file_name"]

if not path.exists(file_name):
    get_data = Tweet_analysis(  querry= querry, limit=limit,
                                save_data=save_status,
                                file_name= file_name )
    
    commond_words = get_data.common_words(100)
    with open (commond_words_file,"w",encoding='utf-8') as f:
        for words in commond_words : 
            f.write(str(words)+"\n")
    

data = pd.read_pickle(file_name)
data.info()
tweets_per_user = data.groupby("User").count()["Tweet"].sort_values( ascending = False )


pass