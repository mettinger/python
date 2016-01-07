#%%  EXPERIMENT FRAMEWORK FOR AWS/S3

#  1.  make directory in mettinger bucket with name "experiment_name"
#  2.  put main python file, "pythonFile", in "experiment_name"
#          ------ pythonFile must write DONE at finish
#             e.g. awsUtils.saveToS3(experimentName + '/' + parameterGroupName + '/DONE','we done here')
#          ------ pythonFile must cope with previous results, e.g. using previousResults.pkl
#  3.  put required data files in mettinger/Data
#  4.  define parameterListDict using (possibly using makeProduct)
#         e.g. parameterListDict = makeProduct({'movePoints':[[10000,5000]],'uctConstant':[1000], 'moveChoiceMethod':['visits'],'alpha':[.01,.1], 'numLoops':[1000], 'selectChildMethod': ['uct'], 'tableName':['analytics.mettinger_let_it_ride']})
#  5.  put experimentDefinition.txt in "experiment_name" using writeExperiment()
#          e.g. writeExperiment('letItRide1', ['HandRanks.dat'], 'letItRideUCT.py', parameterListDict)
#  6.  run e.g. ~/pypy-2.6.0-linux64/bin/pypy /Users/mettinger/GitHub/python-mettinger/awsUtil/awsExperiments.py 'autoExperiment_3' > /var/www/html/videoPokerResults.txt


import sys
# set path for PyPy
sys.path.append('/home/ubuntu/anaconda/lib/python2.7/site-packages')
sys.path.append('/Users/mettinger/anaconda/lib/python2.7/site-packages')

import os
import boto
from boto.s3.key import Key
import copy

import imp
temp = imp.find_module('awsUtils',['/Users/mettinger/GitHub/python-mettinger/awsUtil/'])
awsUtils = imp.load_module('awsUtils',temp[0],temp[1],temp[2])

#%%

# constuct a product dictionary from a parameter dictionar
#     e.g. makeProduct({'a':[1,2], 'b':[4,5], 'c':[7]}) = 
#           [{'a': 1, 'b': 4, 'c': 7, 'parameterGroupName': 'group0'},
#            {'a': 1, 'b': 5, 'c': 7, 'parameterGroupName': 'group1'},
#            {'a': 2, 'b': 4, 'c': 7, 'parameterGroupName': 'group2'},
#            {'a': 2, 'b': 5, 'c': 7, 'parameterGroupName': 'group3'}]

def makeProduct(parameterListDict):
    
    def myUpdate(thisDict,thisKey,thisValue):
        thisDict = copy.deepcopy(thisDict)
        thisDict[thisKey] = thisValue
        return thisDict
        
    if len(parameterListDict) == 1:
        thisKey = parameterListDict.keys()[0]
        parameterDictList = [{thisKey:thisValue} for thisValue in parameterListDict.values()[0]]
    else:
        allItems = parameterListDict.items()
        firstItem = allItems[0]
        remainingItems = dict(allItems[1:])
        recursiveParameterDict = makeProduct(remainingItems)
        thisKey = firstItem[0]
        allValues = firstItem[1]
        parameterDictList = []
        for thisValue in allValues:
            for thisDict in recursiveParameterDict:
                parameterDictList.append(myUpdate(thisDict, thisKey, thisValue))
                
    i = 0            
    for thisDict in parameterDictList:
        thisDict['parameterGroupName'] = 'group' + str(i)
        i = i + 1
    return parameterDictList
    
# write an experiment definition file from list of parameters and other essential information  
def writeExperiment(experimentName, dataFileList, pythonFile, parameterDictList):
    definitionDict = {'experimentName': experimentName, 
                      'datafileList': dataFileList,
                      'pythonFile': pythonFile,
                      'parameterList': parameterDictList}
                      
    # write the experiment definition file
    keyString = experimentName + '/experimentDefinition.txt'
    awsUtils.saveToS3(keyString, str(definitionDict))


#%% RUN AN EXPERIMENT

if len(sys.argv) < 2:
    experimentName = 'letItRide1'
    print "experiment name: " + experimentName
else:
    experimentName = sys.argv[1]
    print "experiment name: " + experimentName
    
# load the experiment definition file
keyString = experimentName + "/experimentDefinition.txt"
definitionDict = eval(awsUtils.loadFromS3(keyString, stringFlag = 1))

datafileList = definitionDict['datafileList']
pythonFile = definitionDict['pythonFile']
parameterList = definitionDict['parameterList']

# load all the data files locally from S3 (if necessary)
for thisDataFile in datafileList:
    if not os.path.exists('/Users/mettinger/Data/' + thisDataFile):
        s3 = boto.connect_s3()
        b = s3.get_bucket('mettinger') 
        k = Key(b)
        k.key = 'Data/' + thisDataFile
        k.get_contents_to_filename('/Users/mettinger/Data/' + thisDataFile)
    
# load the python file from S3
s3 = boto.connect_s3()
b = s3.get_bucket('mettinger') 
k = Key(b)
k.key = experimentName + '/' + pythonFile
k.get_contents_to_filename('/Users/mettinger/Data/' + pythonFile)

# run the experiments
for thisParameters in parameterList:
    # look for 'DONE' flag.  if not found, continue the experiment
    keyString = experimentName + '/' + thisParameters['parameterGroupName'] + '/DONE'
    if not awsUtils.testForKeyS3(keyString):
        print "group name: " + thisParameters['parameterGroupName']
        sys.argv = [experimentName, str(thisParameters)]
        execfile('/Users/mettinger/Data/' + pythonFile)

        






