#%%

import numpy as np
import matplotlib.pyplot as plt
import sklearn as sk
from sklearn import svm
from sklearn import cross_validation

#%% READ THE DATA

f = open("/Users/mettinger/Data/sphereAndCube/sphereCubeData.txt")
data = np.loadtxt(f,delimiter=",")
f.close()

dataShuffled = sk.utils.shuffle(data)

#%%

model = svm.LinearSVC()

#%%

scores = cross_validation.cross_val_score(model, dataShuffled[:,1:],dataShuffled[:,0],cv=5)
print "scores: " + str(scores)

#%% display random image

doFlag = 0
if doFlag == 1:
    testImage = data[12021,1:]
    testImage2 = np.reshape(testImage,(40,40))
    plt.imshow(testImage2)
    
    
