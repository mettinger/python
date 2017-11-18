
# coding: utf-8

#%%


import numpy as np
import random
import matplotlib.pyplot as plt
from multiprocessing import Pool


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
    
# non-overlapping spheres fully contained in unit cube
def makeSpheres(centerSampleFunction, radiusSampleFunction, numSphere):
    spheres = []
    while len(spheres) < numSphere:
        thisTestSphere = (centerSample1(), radiusSampleFunction())
        if np.any(thisTestSphere[0] < thisTestSphere[1]) or np.any(thisTestSphere[0] + thisTestSphere[1] > 1.0):
            continue
        if testSphere(thisTestSphere,spheres):
            spheres.append(thisTestSphere)
    #spheres = [(centerSampleFunction(), radiusSampleFunction()) for i in range(numSphere)]
    return spheres
           

def depthGet(sphereList, cameraPosition, polarAngle, azimuthalAngle, rayLimit):
    
    unitRayVector = np.array([np.cos(azimuthalAngle)*np.sin(polarAngle),
                              np.sin(azimuthalAngle)*np.sin(polarAngle),
                              np.cos(polarAngle)])
    
    distances = []
    intersections = []
    
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
                intersection1 = cameraPosition + (t1 * unitRayVector)
                d1 = np.linalg.norm(intersection1)
            else:
                intersection1 = cameraPosition + (t1 * -unitRayVector)
                d1 = np.linalg.norm(intersection1)
                
            if t2 > 0:
                intersection2 = cameraPosition + (t2 * unitRayVector)
                d2 = np.linalg.norm(intersection2)
            else:
                intersection2 = cameraPosition + (t2 * -unitRayVector)
                d2 = np.linalg.norm(intersection2)
                
            distances.append(d1)
            distances.append(d2)
            
            intersections.append(intersection1)
            intersections.append(intersection2)
            
    if len(distances) == 0:
        return (rayLimit,None)
    else:
        minPosition = np.argmin(distances)
        return (distances[minPosition], intersections[minPosition])
    

def depthMapMake(sphereList, cameraPosition, rayAngleList, rayLimit = 2):
    depthList, intersectionList = list(zip(*[depthGet(sphereList, cameraPosition, polarAngle, azimuthalAngle, rayLimit) for polarAngle, azimuthalAngle in rayAngleList]))
    return depthList, intersectionList

def sphereListTest(thisTuple):
    sphereList, point = thisTuple
    flag = 0
    for center, radius in sphereList:
        if np.linalg.norm(center - np.array(point)) < radius:
            flag = 1
    return flag
        
def sphereVoxelArray(sphereList, numVoxPerSide = 100, numCPU = 1):
    start = 1./(numVoxPerSide * .5)
    end = 1. -  1./(numVoxPerSide * .5)
    a = np.linspace(start, end, numVoxPerSide)
    
    if numCPU > 1:
        pool = Pool(processes=numCPU)  
        voxArray = pool.map(sphereListTest, [(sphereList, (i,j,k)) for i in a for j in a for k in a])
    else:
        voxArray = [sphereListTest((sphereList, (i,j,k))) for i in a for j in a for k in a]
        
    voxArray = np.array(voxArray).reshape((numVoxPerSide, numVoxPerSide, numVoxPerSide))
    return voxArray
    
    
#%%
    
numCPU = 4
numArray = 2

minSpheres = 1
maxSpheres = 10

numSphereList = [random.randint(minSpheres, maxSpheres) for i in range(numArray)]
sphereListList = [list(makeSpheres(centerSample1, radiusSample1, i)) for i in numSphereList]

if numCPU ==1:
    voxArrayList = [sphereVoxelArray(thisList) for thisList in sphereListList]
else:
    pool = Pool(numCPU)
    voxArrayList = pool.map(sphereVoxelArray, sphereListList)

#%%

'''
sphereList = list(makeSpheres(centerSample1, radiusSample1, 30))
voxArray = sphereVoxelArray(sphereList)
'''

#%%

'''
numAzAngle = 300
numPolarAngle = 300

#cameraPosition = np.array([0,0,0])
#rayAngleList = [(azAngle, polarAngle) for azAngle in np.linspace(0,np.pi/2.,numAzAngle) for polarAngle in np.linspace(0,np.pi/2.,numPolarAngle)]

cameraPosition = np.array([0,.5,.5])
rayAngleList = [(azAngle, polarAngle) for azAngle in np.linspace(0.0,np.pi, numAzAngle) for polarAngle in np.linspace(0,np.pi,numPolarAngle)]

depthMap, intersectionList = depthMapMake(sphereList, cameraPosition, rayAngleList)

depthMapArray = np.array(depthMap).reshape((numAzAngle, numPolarAngle))


plt.imshow(depthMapArray, cmap='gray')
plt.ylabel('equal polar angle increments')
plt.xlabel('equal azimuthal angle increments')
'''

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


