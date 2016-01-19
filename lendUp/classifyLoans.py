#%%

import numpy as np
import pandas as pd
from sklearn.preprocessing import Imputer
from sklearn.linear_model import LogisticRegressionCV

#%% READ RAW DATA

dataFile = "/Users/mettinger/Data/lendUp/loanData.csv"
df = pd.read_csv(dataFile)

#%% PREPROCESS THE DATA

# drop some unhelpful features
df1 = df.dropna(subset = ['loan_status'])
dropColumns = ['id','member_id','url','desc','policy_code']
df2 = df1.drop(dropColumns, axis = 1)

# drop categorical columns for the moment and return to them later
dtypes = df2.dtypes
categoricalCols = [i for i in df2.columns if dtypes[i] == 'object']
categoricalCols.remove('loan_status')
df2 = df2.drop(categoricalCols, axis = 1)

# drop features with "too much" missing data
naDropTreshold = 90000
df3 = df2.dropna(axis=1, thresh=naDropTreshold)

# prepare data for scikit-learn models
y = [1 if i == "Fully Paid" else 0 for i in df3['loan_status'].values]
X = df3.ix[:, df3.columns != 'loan_status'].values

# impute values for missing data 
imp = Imputer(strategy='mean', axis=0)
X = imp.fit_transform(X)

#%%

# fit and assess two logistic regression models, using l1 and l2 regularization,
#    using CV to find good hyperparameters
model_l1 = LogisticRegressionCV(penalty='l1', solver='liblinear')
model_l1.fit(X,y)

scores = np.mean(model_l1.scores_[1], axis=0)
score_best_l1 = max(scores)
C_best_l1 = model_l1.Cs_[np.argmax(scores)]

#%%

model_l2 = LogisticRegressionCV(penalty='l2')
model_l2.fit(X,y)

scores = np.mean(model_l2.scores_[1], axis=0)
score_best_l2 = max(scores)
C_best_l2 = model_l2.Cs_[np.argmax(scores)]

if score_best_l2 > score_best_l1:
    print "l2 regularization is better."
    print "best regularization coeff: " + str(C_best_l2)
else:
    print "l1 regularization is better."
    print "best regularization coeff: " + str(C_best_l1)

