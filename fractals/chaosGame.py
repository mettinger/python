#%%

#%matplotlib inline

#%%

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#%%

def functionListGet2d():
    
    def f0(x,y):
        return (x/2., y/2.)
        
    def f1(x,y):
        return ((x+1)/2., y/2.)
        
    def f2(x,y):
        return (x/2., (y+1.)/2.)
        
    functionList = [f0,f1,f2]
    return functionList
    
def functionListGet3d():
    
    def f0(x,y,z):
        return (x/2., y/2., z/2.)
        
    def f1(x,y,z):
        return ((x+1)/2., y/2., z/2.)
        
    def f2(x,y,z):
        return (x/2., (y+1.)/2., z/2.)
        
    def f3(x,y,z):
        return (x/2., y/2., (z+1.)/2.)
        
    functionList = [f0,f1,f2,f3]
    return functionList
    
#%%

def chaosGame2d(numPoints = 100000, exclude = 20, plotFlag=True):
    
    x = np.random.uniform(-1,1)
    y = np.random.uniform(-1,1)
    
    functionList = functionListGet2d()

    i = 0
    xList = []
    yList = []
    
    for i in range(numPoints):
        randomFunction = functionList[np.random.randint(0,3)]
        x,y = randomFunction(x,y)
        if i > exclude:
            xList.append(x)
            yList.append(y)
        i += 1
        
    if plotFlag:
        plt.scatter(xList,yList,s=.001)
        
    return (xList,yList)

def chaosGame3d(numPoints = 1000, exclude = 20, plotFlag=True, size = 20, center=True):
    
    x = np.random.uniform(-1,1)
    y = np.random.uniform(-1,1)
    z = np.random.uniform(-1,1)
    
    functionList = functionListGet3d()

    i = 0
    xList = []
    yList = []
    zList = []
    
    for i in range(numPoints):
        randomFunction = functionList[np.random.randint(0,4)]
        x,y,z = randomFunction(x,y,z)
        if i > exclude:
            xList.append(x)
            yList.append(y)
            zList.append(z)
        i += 1
        
    if center:
        xCenter = np.mean(xList)
        xList = [i - xCenter for i in xList]
        yCenter = np.mean(yList)
        yList = [i - yCenter for i in yList]
        zCenter = np.mean(zList)
        zList = [i - zCenter for i in zList]
        
    if plotFlag:
        fig = plt.figure(figsize=(5,5))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xList,yList,zList,s = size)
        
    return (xList, yList, zList)
    
def project(xList, yList, zList, plotFlag = True, size=20):
    
    xpList = []
    ypList = []
    zpList = []
    
    for i in range(len(xList)):
        thisPoint = (xList[i], yList[i], zList[i])
        norm = np.linalg.norm(thisPoint)
        xpList.append(xList[i]/norm)
        ypList.append(yList[i]/norm)
        zpList.append(zList[i]/norm)
        
    if plotFlag:
        fig = plt.figure(figsize=(5,5))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xpList,ypList,zpList,s = size)
        
    return (xpList, ypList, zpList)
    
#%%

xList, yList, zList = chaosGame3d(numPoints = 10000, size = 1)

#%%

xpList, ypList, zpList = project(xList, yList, zList, size = 1)


