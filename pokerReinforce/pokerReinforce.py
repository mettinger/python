#%% HEADS UP HOLD'EM VIA DEEP REINFORCEMENT LEARNING

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import Adadelta, RMSprop
from keras.utils import np_utils
from keras.models import model_from_json
import numpy as np
from numpy import matlib
import struct
import random
import theano
import boto
from boto.s3.key import Key
import os
import datetime
import sys

#%% define cards and constants

HANDTYPES= [
    "invalid hand",
    "high card",
    "one pair",
    "two pairs",
    "three of a kind",
    "straight",
    "flush",
    "full house",
    "four of a kind",
    "straight flush"]

CARDS= {"2c": 1,"2d": 2,"2h": 3,"2s": 4,"3c": 5,"3d": 6,"3h": 7,"3s": 8,"4c": 9,
        "4d": 10,"4h": 11,"4s": 12,"5c": 13,"5d": 14,"5h": 15,"5s": 16,"6c": 17,
        "6d": 18,"6h": 19,"6s": 20,"7c": 21,"7d": 22,"7h": 23,"7s": 24,"8c": 25,
        "8d": 26,"8h": 27,"8s": 28,"9c": 29,"9d": 30,"9h": 31,"9s": 32,"tc": 33,
        "td": 34,"th": 35,"ts": 36,"jc": 37,"jd": 38,"jh": 39,"js": 40,"qc": 41,
        "qd": 42,"qh": 43,"qs": 44,"kc": 45,"kd": 46,"kh": 47,"ks": 48,"ac": 49,
        "ad": 50,"ah": 51,"as": 52}

cardsOpp = [None,"2c","2d","2h","2s","3c","3d","3h","3s","4c","4d","4h","4s",
            "5c","5d","5h","5s","6c","6d","6h","6s","7c","7d","7h","7s","8c",
            "8d","8h","8s","9c","9d","9h","9s","tc","td","th","ts","jc","jd",
            "jh","js","qc","qd","qh","qs","kc","kd","kh","ks","ac","ad","ah","as"]

fp = open('/Users/mettinger/Data/HandRanks.dat','rb')
a = fp.read()
fp.close()

def evalHand(cards): 
    p = 53;
    for i in range(0,len(cards)):
      p = evalCard(p + cards[i])
    p = evalCard(p)
    handType = p>>12
    #handName = HANDTYPES[handType]
    handRank = p & 0x00000fff
    #value = p
    return (handType, handRank)

def evalCard(card):
    b = a[card * 4:(card*4)+4]
    c = struct.unpack("@I", b)[0]
    return c

def getPayout(cards):
    handType, handRank = evalHand(cards)
    if handType <= 1:
        return 0
    elif handType == 2 and handRank < 1981: # jacks or better
        return 0
    elif handType == 9 and handRank == 10:
        return 800  # royal flush
    else:
        return payouts[handType] 
        
actionCode = {}
for i in range(32):
    actionCode[i] = np.array(np_utils.to_categorical([i],32)[0])
    
cardCode = {}
for i in range(1,53):
    suitCode = np_utils.to_categorical([i % 4],4)[0]
    rankCode = np_utils.to_categorical([(i-1)/4],13)[0]
    totalCode = np.hstack((rankCode,suitCode))
    cardCode[i] = totalCode

def encodeCards(cards):
    handCode = np.zeros(85)
    for i in range(5):
        handCode[i*17:i*17 + 17] = cardCode[cards[i]]
    return handCode
    
# network parameters
handEncodeOneHotSize = (13 + 4) * 5 # 13 rank, 4 suits, 5 cards
numAction = 32 # 2**5 possible discard actions
inputSize = handEncodeOneHotSize + numAction

#%% CONNECT TO S3 AND LOAD TESTING FILES
 
# connect to s3
s3 = boto.connect_s3()
b = s3.get_bucket('mettinger') 
k = Key(b)
  
# local weight filename for upload to s3
tempFilename = '/Users/mettinger/Data/s3_temp_file'
#stateActionArrayFilename = "/Users/mettinger/Data/stateActionArray.pkl"
#blockEquivClassFilename = "/Users/mettinger/Data/blockAndEquivClassRepIndices.pkl"


#%% function definitions
        
def memoryEncode(startCards, action, payout, endCards):
    memoryCode = np.zeros( ((13 + 4) * 5) + 32 + 1 + ((13 + 4) * 5))
    memoryCode[0:85] = encodeCards(startCards)
    memoryCode[85 : 85+32] = actionCode[action]
    memoryCode[85 + 32] = payout
    memoryCode[85 + 32 + 1:] = encodeCards(endCards)
    return memoryCode
    
def selectAction(model,cards,epsilon):
    if random.random() < epsilon:
        return random.randint(0,31)
    else:
        handCode = encodeCards(cards).reshape((1,85))
        netInput = np.hstack((matlib.repmat(handCode,32,1),np_utils.to_categorical(range(32),32)))
        predictions = model.predict(netInput,verbose=0)
        return np.argmax(predictions)
        
def doAction(hand,action):
    playerDiscardCode = '{0:05b}'.format(action)
    cardsToKeep = [hand[i] for i in range(5) if playerDiscardCode[i]== '0']
    remainingDeck = set(range(1,53)) - set(hand)
    newCards = list(random.sample(remainingDeck, 5 - len(cardsToKeep)))         
    hand = cardsToKeep + newCards
    return hand        
    
# TEST FUNCTIONS
def testHand(cards,model):
    if type(cards[0]) is str:
        cards = [CARDS[i] for i in cards]
    handCode = encodeCards(cards).reshape((1,85))
    netInput = np.hstack((matlib.repmat(handCode,32,1),np_utils.to_categorical(range(32),32)))
    predictions = model.predict(netInput,verbose=0)
    return [np.argmax(predictions),predictions]
    
def get_layer_output(layerNum, inputData):
    f = theano.function([model.layers[0].input], model.layers[layerNum].get_output(train=False))
    return f(inputData)
    
def getEstimatedRTP(modelName):
    os.system("python /Users/mettinger/GitHub/python-mettinger/deepReinforcement/videoPokerRTPEstimate.py %s &" % modelName)
    
# LOAD MODEL FROM S3 OR MAKE NEW MODEL IF IT DOESN'T EXIST ON S3
def getModelFromS3orCreate(dataDict):
    
    modelName = dataDict['modelName']
    numReplayMemory = dataDict['numReplayMemory']
    epsilon = dataDict['epsilon']
    optMethod = dataDict['optMethod']
    lossFunction = dataDict['lossFunction']
    architectureFunction = dataDict['architectureFunction']
    
    # s3 keys for weight file and architecture file
    weightKey = modelName + '/model_weights_key'
    architectureKey = modelName + '/architecture_key'
    replayMemoryKey = modelName + '/replayMemory_key'
    validationKey = modelName + '/validation_key'
    
    # load model from s3 if it exists...
    if b.get_key(weightKey) != None:
        print "loading model..."
        k.key = architectureKey
        json_string = k.get_contents_as_string()
        model = model_from_json(json_string)
        
        k.key = weightKey
        k.get_contents_to_filename(tempFilename)
        model.load_weights(tempFilename)
        model.compile(loss=lossFunction, optimizer=optMethod)
        
        k.key = replayMemoryKey
        k.get_contents_to_filename(tempFilename)
        fp = open(tempFilename,"r")
        replayMemory = np.load(fp)
        fp.close()
        
    # ...or make new model
    else:
        print "creating new model..."
        #model = makeDeepNet(inputSize) 
        model = architectureFunction(inputSize)
        model.compile(loss=lossFunction, optimizer=optMethod)
        
        # initialize replay memory
        replayMemory = np.zeros((numReplayMemory, handEncodeOneHotSize + numAction + 1 + handEncodeOneHotSize))
        for i in range(numReplayMemory):
            startCards = random.sample(range(1,53),5)
            action = selectAction(model,startCards,epsilon)
            endCards = doAction(startCards,action)
            payout = getPayout(endCards)
            
            memoryCode = memoryEncode(startCards,action,payout,endCards)
            replayMemory[i,:] = memoryCode
            
        # initialize validation data
        k.key = validationKey
        k.set_contents_from_string(str([]))
        
    return model, replayMemory
    
def saveArchitectureToS3(modelName):
    architectureKey = modelName + '/architecture_key'
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = architectureKey
    json_string = model.to_json()
    k.set_contents_from_string(json_string)
    
def saveWeightsToS3(modelName):
    weightKey = modelName + '/model_weights_key'
    model.save_weights(tempFilename, overwrite=True)
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = weightKey
    k.set_contents_from_filename(tempFilename)

def saveParametersToS3(modelName,dataDictString):
    parameterKey = modelName + '/parameter_key'
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = parameterKey
    k.set_contents_from_string(dataDictString)
    
def saveReplayMemoryToS3(replayMemory):
    replayMemoryKey = modelName + '/replayMemory_key'
    fp = open(tempFilename,"w")
    np.save(fp, replayMemory)
    fp.close()
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = replayMemoryKey
    k.set_contents_from_filename(tempFilename)
    
# ARCHITECTURE FUNCTIONS 
def makeDeepNet_0(inputSize, optMethod):
    model = Sequential()
    model.add(Dense(inputSize, 64, init='uniform'))
    model.add(Activation('tanh'))
    model.add(Dropout(0.5))
    model.add(Dense(64, 64, init='uniform'))
    model.add(Activation('tanh'))
    model.add(Dropout(0.5))
    model.add(Dense(64, 1, init='uniform'))
    model.add(Activation('sigmoid'))
    return model

def makeDeepNet_2(inputSize):
    model = Sequential()
    model.add(Dense(inputSize, 500, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(500, 500, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(500, 1, init='uniform'))
    model.add(Activation('linear'))
    return model
    
def makeDeepNet_1(inputSize):
    model = Sequential()
    model.add(Dense(inputSize, 300, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dense(300, 1, init='uniform'))
    model.add(Activation('linear'))
    return model
    
#%% TRAIN

# how to run: python videoPokerDeepRL.py 'MODELNAME'
modelName = sys.argv[1]

trainFlag = 1
if trainFlag == 1:
    
    # parameters
    #modelName = 'model_3'
    architectureFunction = makeDeepNet_2
    numReplayMemory = 10**6
    numTrain = 10**7
    epsilon = .1
    nb_minibatch = 32
    optMethod = RMSprop() #Adadelta()
    lossFunction = 'mean_squared_error'
    dataDict = {'modelName': modelName, 'numReplayMemory': numReplayMemory, 'numTrain': numTrain,
                'epsilon': epsilon, 'np_minibatch': nb_minibatch, 'optMethod': optMethod,
                'lossFunction' : lossFunction, 'architectureFunction': architectureFunction}
                
    validationPeriod = 10**5 # how often do we kick off validation process
    saveDataPeriod = 10**4 # how often do we save the model and report
    
    print "\nparameters: " + str(dataDict)
    
    # initialize model
    model, replayMemory = getModelFromS3orCreate(dataDict)
    
    # save the architecture and parameters
    saveArchitectureToS3(modelName)
    saveParametersToS3(modelName, str(dataDict))
    
    startTime = datetime.datetime.now()
    print "start: " + str(startTime)
    print "training..."
    for i in range(numTrain):
        
        if i % validationPeriod == 0:
            # calcuate "validation" data
            print "\nvalidating: " + str(datetime.datetime.now())
            getEstimatedRTP(modelName)
            # other validations values, e.g. Q as in deepmind paper?
            
        if i % saveDataPeriod == 0:
            
            #save the weights and replay memory
            saveWeightsToS3(modelName)
            saveReplayMemoryToS3(replayMemory)
            
            # print info periodically
            print "\ntraining pass: " + str(i) + " of " + str(numTrain)
            #print "validation value: " + str(validationValue)
            endTime = datetime.datetime.now()
            print "end: " + str(endTime)
            elapsed = endTime - startTime
            print "elapsed: " + str(elapsed)
            estimatedRemainingTime = (numTrain - (i+1)) * (elapsed/(i+1))
            print "estimated remaining time: " + str(estimatedRemainingTime)
            sys.stdout.flush() # flush the output for monitoring
            
        startCards = sorted(random.sample(range(1,53),5)) # sort the hand is best????
        action = selectAction(model,startCards,epsilon)
        endCards = doAction(startCards,action)
        payout = getPayout(endCards)
        
        # insert into replay memory
        memoryIndex = i % numReplayMemory
        memoryCode = memoryEncode(startCards,action,payout,endCards)
        replayMemory[memoryIndex,:] = memoryCode
        
        #update weights
        replayData = replayMemory[random.sample(range(numReplayMemory),nb_minibatch),:]
        X_train = replayData[:,0:117]
        y_train = replayData[:,117]
        model.fit(X_train, y_train, nb_epoch=10,verbose=0)
    
    #save the weights and replay memory
    saveWeightsToS3(modelName)
    saveReplayMemoryToS3(replayMemory)
    
#%% TESTS
    
flag = 0
if flag == 1:
    hand = ['4d','5d','6d','7d', '8d']
    print testHand(hand,model)
    
flag = 0
if flag == 1:
    layerToExamine = 4
    testData = np.array([1] + [0 for i in range(116)]).reshape((1,117))
    layer_output = get_layer_output(testData)
    print layer_output.shape,layer_output




