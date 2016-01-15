#%%

import pandas as pd
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import Imputer

#%%

df = pd.read_csv("loanData.csv")

#%%

df1 = df.dropna(subset = ['loan_status'])
dropColumns = ['id','member_id','url','desc','policy_code']
df2 = df1.drop(dropColumns, axis = 1)

dtypes = df2.dtypes
categoricalCols = [i for i in df2.columns if dtypes[i] == 'object']
categoricalCols.remove('loan_status')
df2 = df2.drop(categoricalCols, axis = 1)

'''
for col in categoricalCols:
    df2[col] = df2[col].astype('category')
'''

#%%
df3 = df2.dropna(axis=1, thresh=160000)
#df3['loan_status'] = [1 if i == "Fully Paid" else 0 for i in df3['loan_status'].values]

#%%
y = [1 if i == "Fully Paid" else 0 for i in df3['loan_status'].values]
X = df3.ix[:, df3.columns != 'loan_status'].values
imp = Imputer(strategy='mean', axis=0)
X = imp.fit_transform(X)

#%%

model = LogisticRegression()
paramGrid = {'C':[.01,.1,1.,10.,100.]}
clf = GridSearchCV(model, paramGrid)
clf.fit(X, y)

#%%

print "best score: " + str(clf.best_score_)
print "best estimator: " + str(clf.best_estimator_)
print "all scores: "  + str(clf.grid_scores_)
