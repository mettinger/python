#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from numpy import arange, pi, sin, cos, arccos
import plotly.express as px
import pandas as pd
from sklearn.metrics.pairwise import haversine_distances # great circle distances in radians
import dtale

import plotly.io as pio
pio.renderers.default = 'plotly_mimetype+notebook' 

# http://extremelearning.com.au/how-to-evenly-distribute-points-on-a-sphere-more-effectively-than-the-canonical-fibonacci-lattice/


# In[2]:


def pointsOnSphereGet(n):
    i = arange(0, n, dtype=float) + 0.5
    phi = arccos(1 - 2*i/n)
    goldenRatio = (1 + 5**0.5)/2
    theta = 2 * pi * i / goldenRatio
    
    lat = np.pi/2 - phi
    latLong = np.vstack((lat, theta)).transpose()
    
    x, y, z = cos(theta) * sin(phi), sin(theta) * sin(phi), cos(phi);
    xyz = np.vstack((x,y,z)).transpose()
    
    return xyz, latLong

def distanceMatrixGet(pointArray, greatCircleFlag):
    if greatCircleFlag:
        distanceMatrix = haversine_distances(pointArray)
    else:
        nPoints,_ = pointArray.shape
        distanceMatrix = np.zeros(shape=(nOsc, nOsc))
        for i in range(nPoints):
            for j in range(i, nPoints):
                distanceMatrix[i,j] = np.linalg.norm(pointArray[i,:] - pointArray[j,:])
                distanceMatrix[j,i] = distanceMatrix[i,j]
                
    return distanceMatrix


# In[3]:


nOsc = 1000
greatCircleFlag = True

xyz, latLong = pointsOnSphereGet(nOsc)
distanceMatrix = distanceMatrixGet(latLong, greatCircleFlag=greatCircleFlag)


# In[4]:


fig = px.scatter_3d(xyz, x=0,y=1,z=2)
fig.show()


# In[5]:


np.savetxt("./julia/distanceMatrix.csv", distanceMatrix, delimiter=",")
np.save("./julia/pointsOnSphereXYZ.npy", xyz)


# In[6]:


df = pd.DataFrame(distanceMatrix)
dtale.show(df)

# %%
