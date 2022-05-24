from matplotlib.cm import get_cmap
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
#Como en esta base de datos tenemos None y nos nans tenemos que remplazarlos.
data['Account followers'].replace("None", np.nan, inplace=True)



#Separamos los datos del entrenamiento de los del testeo.
instances = len(data)
train_set = data.iloc[0 : int(instances*.8)]
test_set = data.iloc[int(instances*.8):]

#Creamos categorias para el número de followers
data["followers_cat"] = pd.cut( data["Account followers"] ,
                                bins = [0.0, 100. ,1000. ,10000. ,100000. ,np.inf ],
                                labels = [1, 2, 3, 4, 5 ])
#Quitamos las columnas con nans y reseteamos los indices. Buscar otro tratamiento PENDIENTE
cleaned_data=data.dropna(subset=["followers_cat"]).reset_index(drop = True )
cleaned_data.info()

#Creamos una variable que sea el número de interacciones con el tweet.
cleaned_data["Total interactions"] = cleaned_data["Quote count"] + cleaned_data["Reply count"] + cleaned_data["Retweet count"] + cleaned_data["Like count"]


#Distribuyamos los datos de manera uniforme según los seguidores.
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=25)
for train_index, test_index in split.split(cleaned_data, cleaned_data["followers_cat"]):
 strat_train_set = cleaned_data.loc[train_index]
 strat_test_set = cleaned_data.loc[test_index]

#Veamos cuantas muestras tenemos por categoría en el ingreso medio.
print(strat_test_set["followers_cat"].value_counts()) 

#Eliminamos la categoría que acabamos de crear de nuestros data sets.
for item in (strat_test_set, strat_train_set):
    item.drop("followers_cat", axis = 1 , inplace = True)


corr_matrix = cleaned_data.corr()
#Para ver la correlación entre las interacciones y otras cantidades que tenemos podemos quitar el # de la linea inferior.
#print(corr_matrix["Total interactions"].sort_values(ascending = False))

#Comp podemos ver en esta gráfica parece que mientras mas followers mas interacciones tienen los tweets.
cleaned_data.plot(kind = "scatter", x = "followers_cat", y = "Total interactions",
                  alpha = 0.4 , cmap = plt.get_cmap("jet"), c = "Account followers", colorbar = True )
plt.show()

#Aquí copiamos el dataset de prueba sin el total de interacciones que es lo que queremos predecir
cleaned_data = strat_train_set.drop("Total interactions", axis = 1)
#Guardamos el número de interacciones en una lista.
Total_interactions = strat_train_set["Total interactions"].copy()
#Hacemos un data frame con solo valores numéricos.
num_cleaned_data = cleaned_data.drop(["Date", "User", "Tweet", "Account creation"], axis = 1)

pass