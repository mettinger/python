#%%  LEARN THE VELOCITY OF SPHERES FROM DEPTH MAPS PRODUCED IN UNITY

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import random
import os
plt.style.use('ggplot')

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D
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
    
    
# given two times, generate a depth differene image and velocity vector
def getDepthDiffAndVelocity(depthData, locationData, time0, time1):
    return (depthData[time1,:,:] - depthData[time0,:,:], locationData[time1,:] - locationData[time0,:] )
    
# generate arrays for depth difference images and velocity vectors
def getRandomDepthDiffVelocityAndStartPositionMatrix(depthData, locationData, numSamples, cnnFlag):
    numData = depthData.shape[0]
    img_rows = depthData.shape[1]
    img_cols = depthData.shape[2]
    depthDiffArray = np.zeros((numSamples, img_rows * img_cols))
    velArray = np.zeros((numSamples,3))
    startPositionArray = np.zeros((numSamples,3))
    for i in range(numSamples):
        
        time0 = random.randint(0, numData - 1)
        time1 = random.randint(0, numData - 1)
        d = (depthData[time1,:,:] - depthData[time0,:,:]).flatten()
        v = locationData[time1,:] - locationData[time0,:]
        p = locationData[time1,:]
        depthDiffArray[i,:] = d
        velArray[i,:] = v
        startPositionArray[i,:] = p
    # if using a convolutional network then reshape    
    if cnnFlag == 1:
        depthDiffArray = depthDiffArray.reshape(numSamples,1,img_rows,img_cols)
    return (depthDiffArray, velArray, startPositionArray)
 
'''
TO USE THESE COMMENT OUT 'AGG' BACKEND AT TOP

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
'''
    
# construct a deep model
def nnModel(flag):
    
    if flag == 1:
        model = Sequential()
        model.add(Dense(64, input_dim=40000, init='uniform'))
        model.add(Activation('tanh'))
        model.add(Dropout(0.5))
        model.add(Dense(64, init='uniform'))
        model.add(Activation('tanh'))
        model.add(Dropout(0.5))
        model.add(Dense(3, init='uniform'))
        
        model.compile(loss='mean_squared_error', optimizer='adagrad')
        return model
        
    elif flag == 2:
        model = Sequential()
        model.add(Dense(128, input_dim=40000, init='uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(128, init='uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(3, init='uniform'))
        
        model.compile(loss='mean_squared_error', optimizer='adagrad')
        return model
        
    elif flag == 3:
        model = Sequential()
        model.add(Convolution2D(16, 3, 3, border_mode='full', input_shape=(1, 200, 200)))
        model.add(Activation('relu'))
        model.add(Convolution2D(16, 3, 3))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        
        model.add(Convolution2D(16, 3, 3, border_mode='valid'))
        model.add(Activation('relu'))
        model.add(Convolution2D(16, 3, 3))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        
        model.add(Flatten())
        model.add(Dense(256))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        
        model.add(Dense(3))
        
        model.compile(loss='mean_squared_error', optimizer='adagrad')
        return model
        
    elif flag == 4:
        model = Sequential()
        model.add(Convolution2D(16, 3, 3, border_mode='full', input_shape=(1, 200, 200)))
        model.add(Activation('relu'))
        model.add(Convolution2D(16, 3, 3))
        model.add(Activation('relu'))
        
        model.add(Convolution2D(16, 3, 3, border_mode='valid'))
        model.add(Activation('relu'))
        model.add(Convolution2D(16, 3, 3))
        model.add(Activation('relu'))
        
        model.add(Flatten())
        model.add(Dense(256))
        model.add(Activation('relu'))
        
        model.add(Dense(3))
        
        model.compile(loss='mean_squared_error', optimizer='adagrad')
        return model

# calculate the correct target point in R^3
def bulletSphereIntersectionPoint(velocity, startPosition, bulletSpeed):
    numSamples = velocity.shape[0]
    collisionPoint = np.zeros((numSamples,3))
    tol = 10**-6
    for i in range(numSamples):
        p = startPosition[i,:]
        v = velocity[i,:]
        a = np.dot(v,v) - (bulletSpeed**2)
        b = 2 * np.dot(p,v)
        c = np.dot(p,p)
        roots = np.roots([a,b,c])
        if len(roots) == 1:
            collisionTime = roots[0]
        elif roots[0] > 0 and roots[1] > roots[0]:
            collisionTime = roots[0]
        elif roots[1] > 0 and roots[0] > roots[1]:
            collisionTime = roots[1]
        else:
            collisionTime = max(roots)
        
        collisionPoint[i,:] = p  + (v * collisionTime)
        assert abs(np.linalg.norm(collisionPoint[i,:]) - bulletSpeed * collisionTime) < tol
        assert impactDetect(v,p, collisionPoint[i,:],bulletSpeed) == 1
    return collisionPoint

# decide if we hit the sphere (for validation on test set)
def impactDetect(velocity, startPosition, targetPoint, bulletSpeed):
    bulletVelocity = (targetPoint/np.linalg.norm(targetPoint)) * bulletSpeed  
    relativeVelocity = velocity - bulletVelocity
    t0 = (-np.dot(startPosition, relativeVelocity))/ np.dot(relativeVelocity, relativeVelocity)
    sphereCenter = startPosition + (t0 * velocity)
    bulletCenter = t0 * bulletVelocity
    if np.linalg.norm(sphereCenter - bulletCenter) < .5:
        return 1
    else:
        return 0
    
#%%  fit, save and score the model
    
def trainNN():
    
    # define the deep model
    modelFlag = 4
    cnnFlag = 1
    
    # parameters
    bulletSpeed = 100.0
    numSamples = 10**3
    hitArray = []
    
    # frequencies are PER LOOP
    saveFrequency = 1
    scoreFrequency = 1
    numEpochPerLoop = 10
    numLoops = 10000
    
    architectureFilename = '/Users/mettinger/Data/sphereAndCube/model_architecture_' + str(modelFlag) + '.json'
    weightFilename = '/Users/mettinger/Data/sphereAndCube/model_weights_' + str(modelFlag) + '.h5'
    progressFilename = '/Users/mettinger/Data/sphereAndCube/model_progress_' + str(modelFlag) + '.txt'
    plotFilename = '/var/www/html/plot_' + str(modelFlag) + '.png'
    
    # load or make the CNN
    if os.path.exists(architectureFilename): 
        print "loading model..."
        print "model defintion flag: " + str(modelFlag)
        model = model_from_json(open(architectureFilename).read())
        model.load_weights(weightFilename)
    else:
        print "making NEW model..."
        print "model definition flag: " + str(modelFlag)
        model = nnModel(modelFlag)
        
    # MAIN LOOP
    for i in range(numLoops):
        
        # print information
        print "Starting loop %s of %s loops with %s epochs per loop..."  \
                % (str(i + 1), str(numLoops), str(numEpochPerLoop))
        print "Saving the model every %s loops, scoring every %s loops, new data every loop..." \
                % (str(saveFrequency), str(scoreFrequency))
        sys.stdout.flush()
        
        # generate the training data
        print "generating data..."
        sys.stdout.flush()
        X_train, velocityTrain, startPositionArray = \
            getRandomDepthDiffVelocityAndStartPositionMatrix(depthData, 
                                                             locationData, 
                                                             numSamples,
                                                             cnnFlag = cnnFlag)
        Y_train = bulletSphereIntersectionPoint(velocityTrain, startPositionArray, bulletSpeed)                                                             
            
        # fit the model
        print "fitting model..."
        sys.stdout.flush()
        fitHistory = model.fit(X_train, Y_train, 
                               batch_size=32, 
                               nb_epoch=numEpochPerLoop, 
                               verbose = 2, 
                               validation_split = .2) 
        
        # score the model
        if i % scoreFrequency == 0:    
            print "scoring the model..."
            sys.stdout.flush()
            
            X_test, velocityTrain, startPositionArray = \
                getRandomDepthDiffVelocityAndStartPositionMatrix(depthData, 
                                                                 locationData, 
                                                                 numSamples,
                                                                 cnnFlag)
            
            predictions = model.predict(X_test)
            impactBooleans = [impactDetect(velocityTrain[j,:], 
                                           startPositionArray[j,:],
                                           predictions[j,:], 
                                           bulletSpeed)
                              for j in range(numSamples)]
                            
            hitPercentage = np.mean(impactBooleans)
            hitArray.append(hitPercentage)
            print "accuracy: " + str(hitPercentage)
            sys.stdout.flush()
            
        # save the model
        if i % saveFrequency == 0:
            print "saving model..."
            sys.stdout.flush()
            json_string = model.to_json()
            open(architectureFilename, 'w').write(json_string)
            model.save_weights(weightFilename, overwrite=True)
            with open(progressFilename, "a") as myfile:
                myfile.write("loops completed: %s, hit percentage: %s\n" % (str(i), str(hitPercentage)))
            try:
                plt.plot(hitArray)
                plt.ylabel('hit percentage on test set')
                plt.xlabel('loop number')
                plt.title('model code: ' + str(modelFlag))
                plt.savefig(plotFilename)
            except:
                print "plot save failed..."
            
            
    return fitHistory
    
#%% LOAD THE DATA

try:
    depthData
except:
    depthData, locationData = depthAndLocationLoad()
    
#%% TRAIN THE MODEL
    
fitHistory = trainNN()





