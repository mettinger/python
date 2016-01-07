#%%

import numpy as np
import matplotlib.pyplot as plt
import sys
import random
import os
from sklearn import svm
from sklearn import linear_model
from sklearn import cross_validation
plt.style.use('ggplot')

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
#from keras.callbacks import EarlyStopping
from keras.models import model_from_json
    
#%%

# load depth and location data generated in unity
def depthAndLocationLoad():
    numpyFile = "/Users/mettinger/Data/sphereAndCube/depthAndLocation.npz"
    depthFile = "/Users/mettinger/Data/sphereAndCube/depthMaps.txt"
    locationFile = "/Users/mettinger/Data/sphereAndCube/sphereLocationData.txt"
    
    try:
        print "Trying numpy file..."
        sys.stdout.flush() 
        npzfile = np.load(numpyFile)
        locationData = npzfile['arr_1']
        depthData = npzfile['arr_0']
        print "Loaded numpy file..."
    except:    
        print "No numpy data file..."
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
    
# save the depth and location data in numpy format
def numpySave(numpyFilename, depthData, locationData):
    np.savez(numpyFilename, depthData, locationData)
    
# randomly generate a single depth difference image and velocity vector
def getRandomDepthDiffAndVelocity(depthData, locationData):
    numData = depthData.shape[0]
    random1 = random.randint(0, numData - 1)
    random2 = random.randint(0, numData - 1)
    return getDepthDiffAndVelocity(depthData, locationData, random2, random1)
    
# given two times, generate a depth differene image and velocity vector
def getDepthDiffAndVelocity(depthData, locationData, time0, time1):
    return (depthData[time1,:,:] - depthData[time0,:,:], locationData[time1,:] - locationData[time0,:] )

# generate arrays for depth difference images and component velocities    
def getRandomDepthDiffAndVelocityComponentMatrix(depthData, locationData, numSamples, velocityDim):
    depthDiffArray = np.zeros((numSamples, depthData.shape[1]**2))
    velArray = np.zeros(numSamples)
    for i in range(numSamples):
        d,v = getRandomDepthDiffAndVelocity(depthData, locationData)
        depthDiffArray[i,:] = d.flatten()
        velArray[i] = v[velocityDim]
    return (depthDiffArray, velArray)
    
# generate arrays for depth difference images and velocity vectors
def getRandomDepthDiffAndVelocityMatrix(depthData, locationData, numSamples):
    img_rows = depthData.shape[1]
    img_cols = depthData.shape[2]
    depthDiffArray = np.zeros((numSamples, img_rows, img_cols))
    velArray = np.zeros((numSamples,3))
    for i in range(numSamples):
        d,v = getRandomDepthDiffAndVelocity(depthData, locationData)
        depthDiffArray[i,:,:] = d
        velArray[i,:] = v
    depthDiffArray = depthDiffArray.reshape(numSamples,1,img_rows,img_cols)
    return (depthDiffArray, velArray)
 
# display a depth difference image   
def depthDiffImshow(depthDiffMatrix):
    plt.figure()
    plt.imshow(depthDiffMatrix)
    plt.colorbar()
    plt.title("red = t0 and blue = t1")
    
# display a depth image labeled with location  
def depthPlot(depthData, locationData, index):
    testImage = depthData[index,:,:]
    plt.figure()
    plt.imshow(testImage)
    plt.title("index: " + str(index) + " location: " + str(locationData[index,:]))

# get an initialized model    
def getModel(modelFlag):
    if modelFlag == 0:
        epsilon = .1
        max_iter = 10**4
        model = svm.LinearSVR(verbose = 2, epsilon = epsilon, max_iter = max_iter)
    
    elif modelFlag == 1:
        loss = 'epsilon_insensitive'
        epsilon = .01
        model = linear_model.SGDRegressor(epsilon=epsilon, loss = loss)
    return model
    
# get a cross validated score for a model against data X,y
def crossValidate(model,X,y):
    score = 'mean_absolute_error'
    cv = 3
    n_jobs = 1
    scores = cross_validation.cross_val_score(model, X, y, cv=cv, scoring = score, n_jobs = n_jobs)
    print score + ": " + str(scores)
    
# load a keras network
def loadModel():
    architectureFilename = '/Users/mettinger/Data/sphereAndCube/my_model_architecture.json'
    weightFilename = '/Users/mettinger/Data/sphereAndCube/my_model_weights.h5'
    
    print "loading model..."
    model = model_from_json(open(architectureFilename).read())
    model.load_weights(weightFilename)
    return model
    
# construct a convolutional network
def convolutionalNet():
    
    model = Sequential()
    # input: 200x200 images with 1 channel -> (1, 100, 100) tensors.
    # this applies 32 convolution filters of size 3x3 each.
    model.add(Convolution2D(32, 3, 3, border_mode='full', input_shape=(1, 200, 200)))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Convolution2D(64, 3, 3, border_mode='valid'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Flatten())
    # Note: Keras does automatic shape inference.
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(3))
    #model.add(Activation('softmax'))
    
    model.compile(loss='mean_squared_error', optimizer='adagrad')
    return model

# fit, save and score the model
def trainCNN():
    numSamples = 10**4
    
    # frequencies are PER LOOP
    newDataFrequency = 5
    saveFrequency = 1
    scoreFrequency = 1
    numEpochPerLoop = 5
    numLoops = 100
    
    #early_stopping = EarlyStopping(monitor='val_loss', patience=3, verbose=2)
    architectureFilename = '/Users/mettinger/Data/sphereAndCube/my_model_architecture.json'
    weightFilename = '/Users/mettinger/Data/sphereAndCube/my_model_weights.h5'
    
    # load or make the CNN
    if os.path.exists(architectureFilename): 
        print "loading model..."
        model = loadModel()
    else:
        print "making NEW model..."
        model = convolutionalNet()
        
    for i in range(numLoops):
        
        # print information
        print "Starting loop %s of %s loops with %s epochs per loop..."  \
                % (str(i + 1), str(numLoops), str(numEpochPerLoop))
        print "Saving the model every %s loops, scoring every %s loops, new data every %s loops..." \
                % (str(saveFrequency), str(scoreFrequency), str(newDataFrequency))
        sys.stdout.flush()
        
        # generate the training data
        if i % newDataFrequency == 0:
            print "generating data..."
            sys.stdout.flush()
            #X_train, Y_train = getRandomDepthDiffAndVelocityMatrix(depthData, locationData, numSamples)
            randomIndices = np.random.choice(range(depthData.shape[0]),size=numSamples)            
            X_train = depthData[randomIndices,:,:].reshape((numSamples,1,depthData.shape[1],depthData.shape[2]))   
            Y_train = locationData[randomIndices,:]
            
        # fit the model
        print "fitting model..."
        sys.stdout.flush()
        fitHistory = model.fit(X_train, Y_train, batch_size=32, nb_epoch=numEpochPerLoop, verbose = 2, \
                            validation_split = .2) # callbacks=[early_stopping])
                            
        # save the model
        if i % saveFrequency == 0:
            print "saving model..."
            sys.stdout.flush()
            json_string = model.to_json()
            open(architectureFilename, 'w').write(json_string)
            model.save_weights(weightFilename, overwrite=True)
        
        # score the model
        if i % scoreFrequency == 0:    
            print "scoring the model..."
            sys.stdout.flush()
            score = model.evaluate(X_train, Y_train, batch_size=16)
            print "score: " + str(score)
            sys.stdout.flush()
    
    return fitHistory
    
#%% LOAD THE DATA

try:
    depthData
except:
    depthData, locationData = depthAndLocationLoad()
    
#%%
    
trainCNN()

#%% test simple model
    
flag = 0
if flag == 1:
    X = np.array([depthData[i,:,:].flatten() for i in range(depthData.shape[0])])
    y = locationData[:,0]
    
    model = getModel(0)
    crossValidate(model,X,y)


'''
PREP DATA FOR ONE-VELOCITY-COMPONENT MODEL
    
flag = 0
if flag == 1:
    numSamples = 10**5
    velocityDimToPredict = 0
    X, y = getRandomDepthDiffAndVelocityComponentMatrix(depthData, locationData, numSamples, velocityDimToPredict)
'''




