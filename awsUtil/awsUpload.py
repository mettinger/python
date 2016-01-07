#%%
# copy file to AWS EC2 instance

import os
 
#%%
#upload to permanent machine
flag = 1
if flag == 1:
    originString = " /Users/mettinger/Desktop/cudnn-6.5-linux-x64-v2.tgz"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
flag = 0
if flag == 1:
    originString = " /Users/mettinger/Data/vectorBehaviorSimple/vectorBehaviorSimple.npy"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/Users/mettinger/Data/vectorBehaviorSimple/vectorBehaviorSimple.npy"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
#%%    
# download from permanent machine
flag = 0
if flag == 1:
    originString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/Users/mettinger/Data/embeddings.txt"
    destinationString = " /Users/mettinger/Data/embeddings.txt"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
flag = 0
if flag == 1:
    originString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/Users/mettinger/Data/sphereAndCube/my_model_architecture.json"
    destinationString = " /Users/mettinger/Data/sphereAndCube/my_model_architecture.json"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
#%%  
# upload to ARBITRARY machine
flag = 0
if flag == 1:
    awsPublicAddress = "ec2-204-236-141-68.us-west-1.compute.amazonaws.com"
    
    originString = " /Users/mettinger/GitHub/python-mettinger/deepReinforcement/videoPokerDeepRL.py"
    destinationString = " ubuntu@" + awsPublicAddress + ":/home/ubuntu/python"
    scpString = "scp -i ~/.ssh/mettingerGPU.pem" + originString + destinationString
    os.system(scpString)


'''   
# OLD STUFF

flag = 0
if flag == 1:
    originString = " /Users/mettinger/GitHub/python-mettinger/multilevelUserModel/gridFeatures.py"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/python/gridFeatures.py"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
flag = 0
if flag == 1:
    originString = " /Users/mettinger/GitHub/python-mettinger/chrisYu/dailyGameSim2-markCopy.ipynb"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/python/chrisYu/dailyGameSim2-markCopy.ipynb"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
flag = 0
if flag == 1:
    originString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/Users/mettinger/Data/balanceBetDict.pkl"
    destinationString = " /Users/mettinger/Data/balanceBetDict2.pkl"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString) 
    
flag = 0
if flag == 1:
    originString = " /Users/mettinger/GitHub/python-mettinger/jackie/firstDayExperience.ipynb"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/python/jackie"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)

flag = 0
if flag == 1:
    originString = " /Users/mettinger/GitHub/python-mettinger/multilevelUserModel/prepData.py"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/python"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
flag = 0
if flag == 1:
    originString = " /Users/mettinger/GitHub/python-mettinger/multilevelUserModel/combineDatafiles.py"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/python/combineDatafiles.py"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
    originString = " /Users/mettinger/GitHub/r/multilevelUserModel/makeData.R"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/r/multilevelUserModel/makeData.R"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
    
    originString = " /Users/mettinger/GitHub/r/multilevelUserModel/model_2.stan"
    destinationString = " ubuntu@ec2-54-83-50-97.compute-1.amazonaws.com:/home/ubuntu/r/multilevelUserModel/model_2.stan"
    scpString = "scp -i ~/.ssh/mettinger2.pem" + originString + destinationString
    os.system(scpString)
'''