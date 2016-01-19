#%%

import pandas as pd
import matplotlib.pyplot as plt

#%%

def summarizeAndHistogram(dataframe, columnName = 'loan_amnt'):
    print dataframe[columnName].describe()
    
    dataframe[columnName].hist()
    plt.title("histogram for: " + columnName)
    plt.show()
    
#%%

dataFile = "/Users/mettinger/Data/lendUp/loanData.csv"
df = pd.read_csv(dataFile)
summarizeAndHistogram(df)
