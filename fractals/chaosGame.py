#%%

#%matplotlib osx

#%%

import numpy as np
import matplotlib.pyplot as plt

#%%
x = np.random.uniform(-1,1)
y = np.random.uniform(-1,1)

def f0(x,y):
    return (x/2., y/2.)
    
def f1(x,y):
    return ((x+1)/2., y/2.)
    
def f2(x,y):
    return (x/2., (y+1.)/2.)
    
functionList = [f0,f1,f2]

numPoints = 100000
exclude = 50
i = 0
xList = []
yList = []

for i in range(numPoints):
    randomFunction = functionList[np.random.randint(0,3)]
    x,y = randomFunction(x,y)
    if i > exclude:
        xList.append(x)
        yList.append(y)
    i += 1
                      
#%%

plt.scatter(xList,yList,s=.001)


