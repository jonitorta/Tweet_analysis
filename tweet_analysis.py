import pandas as pd
import numpy as np
from tweet_scrapper import Tweet_analysis
from config_file import options
from os import path
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.base import BaseEstimator, TransformerMixin
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


 
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
        
        new_frame = X.copy()
        #En esta parte hacemos la lista con el número total de interacciones
        if self.add_total_interactions:
            total_interactions = X["Reply count"] + X["Retweet count"] + X["Like count"] + X["Quote count"]
            new_frame = np.c_[new_frame, total_interactions]
        #En esta parte contamos el número de palabras y las guardamos ese número en una lista
        if self.add_total_words :
            total_words =  []
            
            for tweets_tex in X["Tweet"]:
                word_list = tweets_tex.split()
                total_words.append( len(word_list) )
            new_frame = np.c_[new_frame, total_words]
            
            
        #En esta parte contamos el tiempo en días desde la creación de la cuenta hasta el día de hoy.
        if self.add_time_plataform:
            today = datetime.now()
            creation_date = X["Account creation"]
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


#Creamos una variable que sea el número de interacciones con el tweet.
data["Total interactions"] = data["Quote count"] + data["Reply count"] + data["Retweet count"] + data["Like count"]

#Creamos categorias para el impacto del tweet
data["Impact"] = pd.cut( data["Total interactions"] ,
                                bins = [-np.inf, 100. ,1000. ,10000. ,100000. ,np.inf ],
                                labels = [1, 2, 3, 4, 5 ])
#Quitamos las columnas con nans y reseteamos los indices. Buscar otro tratamiento PENDIENTE
cleaned_data=data.dropna(subset=["Account followers"]).reset_index(drop = True )
cleaned_data.info()


#Distribuyamos los datos de manera uniforme según el impacto del tweet.
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=25)
for train_index, test_index in split.split(cleaned_data, cleaned_data["Impact"]):
 strat_train_set = cleaned_data.loc[train_index]
 strat_test_set = cleaned_data.loc[test_index]

#Veamos cuantas muestras tenemos por categoría
#print(strat_test_set["Impact"].value_counts()) 

#Eliminamos la categoría que acabamos de crear de nuestros data sets.
for item in (strat_test_set, strat_train_set):
    item.drop("Impact", axis = 1 , inplace = True)


corr_matrix = cleaned_data.corr()
#Para ver la correlación entre las interacciones y otras cantidades que tenemos podemos quitar el # de la linea inferior.
#print(corr_matrix["Total interactions"].sort_values(ascending = False))

#Veamos el impacto de los tweets segun el número de followers.
cleaned_data.plot(kind = "scatter", x = "Account followers", y = "Impact",
                  alpha = 0.4 , cmap = plt.get_cmap("jet"), c = "Account friends", colorbar = True )
plt.show()

#Aquí copiamos el dataset de prueba sin el total de interacciones que es lo que queremos predecir
cleaned_data = strat_train_set.drop("Account followers", axis = 1)
#Guardamos el número de interacciones en una lista.
total_followers = strat_train_set["Account followers"].copy()
#Hacemos un data frame con solo valores numéricos.
num_cleaned_data = cleaned_data.drop(["Date", "User", "Tweet", "Account creation"], axis = 1)



#Pongo falso en total interactions ya que ya las agrege de manera manual, las agregé en el transformador solo para prácticar.
num_pipeline = Pipeline([
( "attribs_adder", CombinedAttributersAdder(add_total_interactions=False, add_time_plataform=False, add_total_words=False) ),
("std_scaler", StandardScaler() ) #Estandarizamos que es restar la media y dividir por la desviación estandar.
])
#Creamos otra pipeline para los atributos categóricos.
cat_pipleline = Pipeline([
    ("attribs_adder", CombinedAttributersAdder(add_total_interactions=False, add_time_plataform=True, add_total_words=True))
])

num_attr = list(num_cleaned_data)
cat_attr = ["Date", "User", "Tweet", "Account creation"]
#Definimos la transformación aplicando ambas pipelines.
full_pipeline = ColumnTransformer([
    ("num", num_pipeline, num_attr),
    ("cat", cat_pipleline, cat_attr)
])
#Hacemos la transformación de todo nuestro data frame
prepared_data = full_pipeline.fit_transform(cleaned_data)
#Declaramos una regresión linearl
lin_reg = LinearRegression()
#Para la regresión lineal solo usaremos en este caso las variables numéricas.
num_prepared_data = prepared_data[ :,[0,1,2,3,-2,-1] ]
#Hacemos el fit.
lin_reg.fit(num_prepared_data, total_followers )

some_data = cleaned_data.iloc[:7]
some_labels = total_followers.iloc[:7]
some_data_prepared = full_pipeline.transform(some_data)
some_num_prepared_data = some_data_prepared[ :,[0,1,2,3,-2,-1] ]

print("Predictions:", lin_reg.predict(some_num_prepared_data))
print("Labels:", list(some_labels))

interactions_prediction = lin_reg.predict(num_prepared_data)
lin_mse = mean_squared_error(total_followers, interactions_prediction)
lin_rmse = np.sqrt(lin_mse)
print(lin_rmse)

from sklearn.model_selection import cross_val_score
scores = cross_val_score(lin_reg, num_prepared_data, total_followers,
 scoring="neg_mean_squared_error", cv=10)
tree_rmse_scores = np.sqrt(-scores)
print(tree_rmse_scores)


pass