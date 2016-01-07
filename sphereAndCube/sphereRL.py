#%%  LEARN THE VELOCITY OF SPHERES FROM DEPTH MAPS PRODUCED IN UNITY USING 
#      DEEP DETERMINISTIC POLICY GRADIENT (DDPG)
#      ref: "CONTINUOUS CONTROL WITH DEEP REINFORCEMENT LEARNING"

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import random
import tensorflow as tf
import scipy.sparse
import os
plt.style.use('ggplot')

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
    
    
# given two times, generate a depth difference image and velocity vector
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

#%% LOAD THE DATA

try:
    depthData
except:
    depthData, locationData = depthAndLocationLoad()
    
#%% Create the models
numPixel = 40000
spatialDim = 3
replaySize = 10**6

actor_x = tf.placeholder("float", [None, numPixel])
actor_W = tf.Variable(tf.random_uniform([numPixel, spatialDim], -1.0, 1.0))
actor_b = tf.Variable(tf.zeros([spatialDim]))
actor_y = tf.matmul(actor_x, actor_W) + actor_b

critic_x_state = tf.placeholder("float", [None, numPixel])
critic_x_action = tf.placeholder("float", [None, spatialDim])
critic_x = tf.concat(1,[critic_x_state,critic_x_action])
critic_W = tf.Variable(tf.zeros([numPixel + spatialDim, 1]))
critic_b = tf.Variable(tf.zeros([1]))
critic_y = tf.matmul(critic_x, critic_W) + critic_b

replayStateMemory = scipy.sparse.rand(replaySize,numPixel, density = .001, format = 'lil')
replayActionMemory = np.zeros((replaySize, spatialDim))
replayRewardMemory = np.zeros((replaySize, 1))

# train the critic
critic_y_ = tf.placeholder("float", [None, 1])
critic_loss = tf.reduce_mean(tf.square(critic_y_ - critic_y))
critic_train_step = tf.train.GradientDescentOptimizer(0.01).minimize(critic_loss)

#critic 2
critic_2_x = tf.placeholder("float", [None, numPixel])
critic_2_action = tf.matmul(critic_2_x, actor_W) + actor_b
critic_2_z = tf.concat(1,[critic_2_x,critic_2_action])
critic_2_y = tf.matmul(-1 * critic_2_z, critic_W) + critic_b # -1 because we want to maximize

# train the actor
actor_train_step = tf.train.GradientDescentOptimizer(0.01).minimize(critic_2_y, var_list = [actor_W, actor_b])

#%% TRAIN THE MODEL

saver = tf.train.Saver()

sess = tf.InteractiveSession()    
tf.initialize_all_variables().run()

'''
init = tf.initialize_all_variables().run()
sess = tf.Session()
'''

bulletSpeed = 100.0
minibatchSize = 32
numStateSamples = 1000
scoreFrequency = 100
saveFrequency = 100
numTestSamples = 1000
hitArray = []
plotFilename = '/var/www/html/plot_DDPG.png'
modelFilename = '/Users/mettinger/Data/sphereAndCube/ddpgModel.ckpt'

if os.path.exists(modelFilename): 
    print "loading model..."
    saver.restore(sess, modelFilename)
else:
    print "creating NEW model..."

replayIndex = 0
for i in range(numStateSamples):
    
    if i % 100 == 0:
        print "sample %s of %s" % (str(i), str(numStateSamples))
        sys.stdout.flush()
        
    # get a random state
    X_train, velocityTrain, startPositionArray = \
        getRandomDepthDiffVelocityAndStartPositionMatrix(depthData, 
                                                         locationData, 
                                                         numSamples = 1,
                                                         cnnFlag = 0)
    thisState = X_train[0].reshape((1,numPixel))
    # get action for the state
    thisAction = actor_y.eval({actor_x: thisState})
    # get reward for the action
    thisReward = impactDetect(velocityTrain[0], startPositionArray[0], thisAction.reshape((3,)), bulletSpeed)
    # store state, action, reward in replay memory        
    replayStateMemory[replayIndex,:] = thisState
    replayActionMemory[replayIndex,:] = thisAction
    replayRewardMemory[replayIndex] = thisReward
    replayIndex = (replayIndex + 1) % replaySize
    # sample replay memory
    sampleIndices = np.random.choice(range(replaySize), minibatchSize, replace=False)
    stateSample = replayStateMemory[sampleIndices,:].toarray()
    actionSample = replayActionMemory[sampleIndices,:]
    rewardSample = replayRewardMemory[sampleIndices]
    
    # update critic
    critic_training_data = np.hstack((stateSample,actionSample))
    critic_train_step.run({critic_x: critic_training_data, critic_y_: rewardSample})
    
    # update actor
    actor_train_step.run({critic_2_x: stateSample})
    
    # score the model
    if i % scoreFrequency == 0:    
        print "scoring the model..."
        sys.stdout.flush()
        
        X_test, velocityTrain, startPositionArray = \
            getRandomDepthDiffVelocityAndStartPositionMatrix(depthData, 
                                                             locationData, 
                                                             numTestSamples,
                                                             cnnFlag = 0)
        
        predictions = actor_y.eval({actor_x:X_test})
        impactBooleans = [impactDetect(velocityTrain[j,:], 
                                       startPositionArray[j,:],
                                       predictions[j,:], 
                                       bulletSpeed)
                          for j in range(numTestSamples)]
                        
        hitPercentage = np.mean(impactBooleans)
        hitArray.append(hitPercentage)
        print "accuracy: " + str(hitPercentage)
        sys.stdout.flush()
        
        try:
            plt.plot(hitArray)
            plt.ylabel('hit percentage on test set')
            plt.xlabel('loop number')
            plt.title('deep deterministic policy gradient')
            plt.savefig(plotFilename)
        except:
            print "plot save failed..."
        
    
    # save the model
    if i % saveFrequency == 0:
        print "saving model..."
        sys.stdout.flush()
        save_path = saver.save(sess, modelFilename)
       
       