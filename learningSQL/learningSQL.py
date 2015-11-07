#%%

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

import numpy as np
import pandas as pd
from pandasql import sqldf

#%%

# generate a random table of integers
def randomTable(numRows, numCols, numItems, columnNames):
    return pd.DataFrame(np.random.randint(0, numItems, size = (numRows,numCols)), columns = columnNames, dtype=int)
    
# do sql query on pandas dataframe
def doQuery(query):
    return sqldf(query, globals())
    
    
#%% generate random tables and query results
    
query = "select col0 from thisTable where col1 = 0"
numSamples = 10
tableRows = 10
tableColumns = 10
numItems = 20
columnNames = ["col" + str(i) for i in range(tableColumns)]
X_train = np.zeros((numSamples, tableColumns * tableRows), dtype = int)
for i in range(numSamples):
    thisTable = randomTable(tableRows, tableColumns, numItems, columnNames)
    X_train[i,:] = thisTable.values.flatten()
    queryResult = doQuery(query).values.flatten().astype(int)
    print queryResult
    
    
    
#%%
model = Sequential()
model.add(Embedding(max_features, 256, input_length=maxlen))
model.add(LSTM(output_dim=128, activation='sigmoid', inner_activation='hard_sigmoid'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='rmsprop')

model.fit(X_train, Y_train, batch_size=16, nb_epoch=10)
score = model.evaluate(X_test, Y_test, batch_size=16)