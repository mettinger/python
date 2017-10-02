
# coding: utf-8

#%%


import numpy as np
import random
import matplotlib.pyplot as plt


#%%

# uniform in the unit cube
def centerSample1():
    center = [random.random() for i in range(3)]
    return np.array(center)

def radiusSample1(low = .05, high=.2):
    return np.random.uniform(low,high)

def testSphere(thisTestSphere, sphereList):
    for thisSphere in sphereList:
        if np.linalg.norm((thisSphere[0] - thisTestSphere[0])**2) < (thisSphere[1] + thisTestSphere[1]) ** 2:
            return False
    return True
    
# non-overlapping spheres
def makeSpheres(centerSampleFunction, radiusSampleFunction, numSphere):
    spheres = []
    while len(spheres) < numSphere:
        thisTestSphere = (centerSample1(), radiusSampleFunction())
        if testSphere(thisTestSphere,spheres):
            spheres.append(thisTestSphere)
    #spheres = [(centerSampleFunction(), radiusSampleFunction()) for i in range(numSphere)]
    return spheres
           

def depthGet(sphereList, cameraPosition, polarAngle, azimuthalAngle, rayLimit):
    
    unitRayVector = np.array([np.cos(azimuthalAngle)*np.sin(polarAngle),
                              np.sin(azimuthalAngle)*np.sin(polarAngle),
                              np.cos(polarAngle)])
    
    distances = []
    
    for thisCenter, thisRadius in sphereList:
        v = cameraPosition - thisCenter
        a = np.dot(v, unitRayVector)
        b = np.dot(v,v) - thisRadius**2
        
        c = a**2 - b
        
        if c < 0:
            continue
        else:
            t1 = -a + np.sqrt(c)
            t2 = -a - np.sqrt(c)
            
            if t1 > 0:
                intersection = cameraPosition + (t1 * unitRayVector)
                d1 = np.linalg.norm(intersection)
            else:
                intersection = cameraPosition + (t1 * -unitRayVector)
                d1 = np.linalg.norm(intersection)
                
            if t2 > 0:
                intersection = cameraPosition + (t2 * unitRayVector)
                d2 = np.linalg.norm(intersection)
            else:
                intersection = cameraPosition + (t2 * -unitRayVector)
                d2 = np.linalg.norm(intersection)
                
            distances.append(d1)
            distances.append(d2)
            
    if len(distances) == 0:
        return rayLimit
    else:
        return min(distances)
    

def depthMapMake(sphereList, cameraPosition, rayAngleList, rayLimit = 2):
    depthList = [depthGet(sphereList, cameraPosition, polarAngle, azimuthalAngle, rayLimit) for polarAngle, azimuthalAngle in rayAngleList]
    return depthList


#%%

sphereList = list(makeSpheres(centerSample1, radiusSample1, 30))
#sphereList = [(np.array([1.0,0.0,1.0]),.25)]

#%%

numAzAngle = 300
numPolarAngle = 300

#cameraPosition = np.array([0,0,0])
#rayAngleList = [(azAngle, polarAngle) for azAngle in np.linspace(0,np.pi/2.,numAzAngle) for polarAngle in np.linspace(0,np.pi/2.,numPolarAngle)]

cameraPosition = np.array([0,.5,.5])
rayAngleList = [(azAngle, polarAngle) for azAngle in np.linspace(0.0,np.pi, numAzAngle) for polarAngle in np.linspace(0,np.pi,numPolarAngle)]

depthMap = depthMapMake(sphereList, cameraPosition, rayAngleList)

depthMapArray = np.array(depthMap).reshape((numAzAngle, numPolarAngle))

#%%

plt.imshow(depthMapArray, cmap='gray')
plt.ylabel('equal polar angle increments')
plt.xlabel('equal azimuthal angle increments')


'''
def depthGet(sphereList, cameraPosition, polarAngle, azimuthalAngle, step, rayLimit):
    
    unitRayVector = np.array([np.cos(azimuthalAngle)*np.sin(polarAngle),
                              np.sin(azimuthalAngle)*np.sin(polarAngle),
                              np.cos(polarAngle)])
    
    for thisRadius in np.arange(0.0, rayLimit, step):
        thisRayPosition = cameraPosition + (thisRadius * unitRayVector)
        for thisSphere in sphereList:
            if np.sum((thisRayPosition - thisSphere[0])**2) <  thisSphere[1]**2:
                return np.linalg.norm(thisRayPosition)
    return rayLimit 
'''


