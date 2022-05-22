import pandas as pd
import numpy as np
from tweet_scrapper import Tweet_analysis
from config_file import options
from os import path
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.impute import SimpleImputer


#Tomamos las opciones.
querry = options["querry"]
limit = options["limit"]
save_status = options["save status"]
file_name = options["file name"]
commond_words_file = options["commond_word_file_name"]

#Si no tenemos la base de datos la descargamos.
if not path.exists(file_name):
    Tweets = Tweet_analysis(  querry= querry, limit=limit,
                                save_data=save_status,
                                file_name= file_name )
    get_data = Tweets.get_tweets()
    #Guardamos en un archivo de texto las 100 palabras mas comunes.
    commond_words = Tweets.common_words(100)
    with open (commond_words_file,"w",encoding='utf-8') as f:
        for words in commond_words : 
            f.write(str(words)+"\n")

#Creamos nuestro data frame.
data = pd.read_pickle(file_name)
data.info()

#Separamos los datos del entrenamiento de los del testeo.
instances = len(data)
train_set = data.iloc[0 : int(instances*.8)]
test_set = data.iloc[int(instances*.8):]

#Veamos como se distribuyen nuestros datos
resume_data = data.describe()
#Creamos categorias para el número de followers
print((data["Account followers"]-data["Account followers"].mean() )/data["Account followers"].std())
data["followers_cat"] = pd.cut( (data["Account followers"]-data["Account followers"].mean() )/data["Account followers"].std() ,
                                bins = [0., 0.2 ,0.4 ,0.6 ,0.8, np.inf ],
                                labels = [1, 2, 3, 4, 5 ])


#Distribuyamos los datos de manera uniforme segund los seguidores.
split = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=15 )
l = split.split(data, data["Account followers"])
for train_index , test_index in split.split(data, data["Account followers"]):
    strat_train_set = data.loc[train_index]
    strat_test_set = data.loc[test_index]



pass