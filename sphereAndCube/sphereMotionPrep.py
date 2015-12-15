#%%

import numpy as np
import matplotlib.pyplot as plt
import sys
import random
from sklearn import svm
from sklearn import cross_validation
plt.style.use('ggplot')

numpyFile = "/Users/mettinger/Data/sphereAndCube/depthAndLocation.npz"
depthFile = "/Users/mettinger/Data/sphereAndCube/depthMaps.txt"
locationFile = "/Users/mettinger/Data/sphereAndCube/sphereLocationData.txt"

#%%

def depthAndLocationLoad():
    try:
        print "Trying numpy file..."
        sys.stdout.flush() 
        npzfile = np.load(numpyFile)
        locationData = npzfile['arr_1']
        depthData = npzfile['arr_0']
        print "Loaded numpy file..."
    except:    
        print "No pickle file..."
        print "Reloading text files..."
        sys.stdout.flush() 
        depthData = np.loadtxt(depthFile,delimiter=",")
        locationData = np.loadtxt(locationFile, delimiter=",")
        
        width = int(locationData[0,0])
        height = int(locationData[0,1])
        locationData = locationData[1:,:]
        
        numSamples = depthData.shape[0]
        
        depthData = depthData.reshape((numSamples,height,width),order='C')
        print "Text files loaded..."
    return (depthData, locationData)
    
def numpySave(numpyFilename, depthData, locationData):
    np.savez(numpyFilename, depthData, locationData)
    
def getRandomDepthDiffAndVelocity(depthData, locationData):
    numData = depthData.shape[0]
    random1 = random.randint(0, numData - 1)
    random2 = random.randint(0, numData - 1)
    return getDepthDiffAndVelocity(depthData, locationData, random2, random1)
    
def getDepthDiffAndVelocity(depthData, locationData, time0, time1):
    return (depthData[time1,:,:] - depthData[time0,:,:], locationData[time1,:] - locationData[time0,:] )
    
def getRandomDepthDiffAndVelocityMatrix(depthData, locationData, numSamples, velocityDim):
    depthDiffArray = np.zeros((numSamples, depthData.shape[1]**2))
    velArray = np.zeros(numSamples)
    for i in range(numSamples):
        d,v = getRandomDepthDiffAndVelocity(depthData, locationData)
        depthDiffArray[i,:] = d.flatten()
        velArray[i] = v[velocityDim]
    return (depthDiffArray, velArray)
    
def depthDiffImshow(depthDiffMatrix):
    plt.figure()
    plt.imshow(depthDiffMatrix)
    plt.colorbar()
    plt.title("red = t0 and blue = t1")
    
def depthPlot(depthData, locationData, index):
    testImage = depthData[index,:,:]
    plt.figure()
    plt.imshow(testImage)
    plt.title("index: " + str(index) + " location: " + str(locationData[index,:]))
    

#%%

try:
    depthData
except:
    depthData, locationData = depthAndLocationLoad()
    
#%%
    
numSamples = 10**5
velocityDimToPredict = 0
X, y = getRandomDepthDiffAndVelocityMatrix(depthData, locationData, numSamples, velocityDimToPredict)

#%%

epsilon = .01
max_iter = 10**4
model = svm.LinearSVR(verbose = 2, epsilon = epsilon, max_iter = max_iter)


#%%

print "fitting model.."
sys.stdout.flush()
model.fit(X,y)
print "R2: " + str(model.score(X,y))
sys.stdout.flush()

#%%

scores = cross_validation.cross_val_score(model, X, y, cv=5)
print "scores: " + str(scores)

