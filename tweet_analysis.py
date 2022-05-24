import pandas as pd
import numpy as np
from tweet_scrapper import Tweet_analysis
from config_file import options
from os import path
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.base import BaseEstimator, TransformerMixin
from datetime import datetime, tzinfo
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer


#Asignamos el número de índice de las varaibles para el transformador
tweet_ix, reply_ix, retweet_ix, like_ix, quote_ix, follower_ix, friend_ix, creation_ix = 2, 3, 4, 5, 6, 7, 8, 9 
#Creamos una clase para hacer atributos nuevos a nuestro data frame
class CombinedAttributersAdder(BaseEstimator, TransformerMixin):
    def __init__(self, add_total_interactions = True, add_total_words = True, add_time_plataform = True ):
        self.add_total_interactions = add_total_interactions
        self.add_total_words = add_total_words
        self.add_time_plataform = add_time_plataform
    #Declaramos este método para que nuestra clase funcione como un transformador
    def fit(self, X , y = None):
        return self
    
    def transform(self, X, y= None):
        
        #En esta parte hacemos la lista con el número total de interacciones
        if self.add_total_interactions:
            total_interactions = X[:, reply_ix] + X[:, retweet_ix] + X[:, like_ix] + X[:, quote_ix]
            new_frame = np.c_[X,total_interactions]
        #En esta parte contamos el número de palabras y las guardamos ese número en una lista
        if self.add_total_words :
            total_words =  []
            print(len(X[:, tweet_ix]))
            for tweets_tex in X[:, tweet_ix]:
                word_list = tweets_tex.split()
                total_words.append( len(word_list) )
            new_frame = np.c_[new_frame, total_words]
            
            
        #En esta parte contamos el tiempo en días desde la creación de la cuenta hasta el día de hoy.
        if self.add_time_plataform:
            today = datetime.now()
            creation_date = X[:, creation_ix]
            days = []
            for dates in creation_date:
                time_up = today - dates.replace(tzinfo=None)
                days.append(time_up.days)
            new_frame = np.c_[new_frame, days]
        
        

        return new_frame


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
#print(strat_test_set["followers_cat"].value_counts()) 

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

#Ahora  tenemos nuestros atributos nuevos agregados.
#attr_adder = CombinedAttributersAdder(add_total_interactions=True,add_time_plataform=True,add_total_words=True)
#data_extra_attr = attr_adder.transform(cleaned_data.values)

#Pongo falso en total interactions ya que ya las agrege de manera manual, las agregé en el transformador solo para prácticar.
num_pipeline = Pipeline([
( "attribs_adder", CombinedAttributersAdder(add_total_interactions=False) ),
("std_scaler", StandardScaler() )
])

num_attr = list(num_cleaned_data)
cat_attr = ["Date", "User", "Tweet", "Account creation"]




pass