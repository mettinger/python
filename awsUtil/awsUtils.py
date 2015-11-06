#%%  EXPERIMENT FRAMEWORK FOR S3, INCLUDING CHECKPOINTING

import boto
import boto.ec2
from boto.s3.key import Key
import random
import os
import cPickle as pickle

'''
HOW TO IMPORT INTO A SCRIPT

import imp
temp = imp.find_module('awsUtils',['/Users/mettinger/GitHub/python-mettinger/awsUtil/'])
awsUtils = imp.load_module('awsUtils',temp[0],temp[1],temp[2])
'''

#%%

def completedExperimentsFind():
    # connect to s3
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    return [str(a.name)[0:-5] for a in list(b.list()) if a.name[-4:]=='DONE']
    
def saveToS3(keyString, objectToStore):
    # connect to s3
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = keyString
    
    if isinstance(objectToStore, str):
        try:
            k.set_contents_from_string(objectToStore)
        except:
            print "s3 write failure"
            return "s3 write failure"
    else:
        try:
            tempFilename = '/Users/mettinger/Data/tempfile' + str(random.randint(0,10000))
            fp = open(tempFilename,"w")
            pickle.dump(objectToStore,fp)
            fp.close()
            k.set_contents_from_filename(tempFilename)
            os.remove(tempFilename)
        except:
            print "s3 write failure"
            return "s3 write failure"

def loadFromS3(keyString, stringFlag = 0):
    # connect to s3
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    k = Key(b)
    k.key = keyString
    if b.get_key(keyString) == None:
        print "bad key"
        return None
        
    # if stringFlag load as string...
    if stringFlag:
        try:
            stringObjFromS3 = k.get_contents_as_string()
            return stringObjFromS3
        except:
            print "s3 string read failure"
            return "s3 string read failure"
    #...otherwise load via temporary file
    else:
        try:
            tempFilename = '/Users/mettinger/Data/tempfile' + str(random.randint(0,10000))
            k.get_contents_to_filename(tempFilename)
            fp = open(tempFilename,"r")
            objectFromS3 = pickle.load(fp)
            fp.close()
            os.remove(tempFilename)
            return objectFromS3
        except:
            print "s3 read pickle failure"
            return "s3 read pickle failure"
            
def testForKeyS3(keyString):
    s3 = boto.connect_s3()
    b = s3.get_bucket('mettinger') 
    if b.get_key(keyString) != None:
        return True
    else:
        return False

def getExperiment(experimentName):
    keyString = experimentName + '/previousResults.pkl'
    # if this experiment already stored results on S3...
    if testForKeyS3(keyString) != None:
        print "loading previous data..."
        previousResults = loadFromS3(keyString, stringFlag = 0)
        return previousResults
    # ....otherwise start a fresh experiment.
    else:
        print "you ned to start fresh..."
        return None

def spotInstanceGet(price = .1, gpuAMIid = 'ami-0b90514f'):
    conn = boto.ec2.connect_to_region("us-west-1")
    instance_type = 'g2.2xlarge' # 1 GPU
    security_group_id = 'launch-wizard-1' # permits ssh
    conn.request_spot_instances(
            price = price,
            image_id = gpuAMIid,
            instance_type=instance_type,
            security_groups=[security_group_id])
    return conn
            
def onDemandInstanceGet(gpuAMIid = 'ami-c54e8a81'):
    conn = boto.ec2.connect_to_region("us-west-1")
    instance_type = 'g2.2xlarge' # 1 GPU
    security_group_id = 'launch-wizard-1' # permits ssh
    
    conn.run_instances(
            image_id = gpuAMIid,
            instance_type=instance_type,
            security_groups=[security_group_id])
    return conn
    
def getIPaddress(conn):
    
    # CAREFUL!!  ASSUMES ONLY ONE ACTIVE INSTANCE TO GET SINGLE IP
    reservations = conn.get_all_reservations()
    instances = [thisInstance for thisRes in reservations for thisInstance in thisRes.instances]
    allActiveIPs = [str(thisInstance.ip_address) for thisInstance in instances if thisInstance.ip_address != None]
    ip = allActiveIPs[0]
    ip = ip.replace('.','-')
    awsPublicAddress = "ec2-" + ip + ".us-west-1.compute.amazonaws.com"
    
    sshString = "ssh -i ~/.ssh/mettingerGPU.pem ubuntu@" + awsPublicAddress
    print "ssh string: "
    print sshString
    return awsPublicAddress
            
            
            
            
            
            
            