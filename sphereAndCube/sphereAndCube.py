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

#%% display random image

testImage = data[12010,1:]
testImage2 = np.reshape(testImage,(40,40))
plt.imshow(testImage2)

#%%

model = svm.LinearSVC()

#%%

scores = cross_validation.cross_val_score(model, dataShuffled[:,1:],dataShuffled[:,0])
