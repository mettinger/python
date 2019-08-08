#!/usr/bin/env python
# coding: utf-8

# In[27]:


import pyautogui
import time
from subprocess import call
import os
from PIL import Image


# In[31]:


upperCornerX = 100
upperCornerY = 50
lowerCornerX = 1600
lowerCornerY = 1020

clickX = 1630
clickY = upperCornerY
startPause = 5
imageFolder = "/Users/mettinger/Data/kindle/"


# In[34]:


pngFileList = [thisFile for thisFile in os.listdir(imageFolder) if thisFile.endswith(".png")]
for thisFile in pngFileList:
    print("removing: " + thisFile)
    os.remove(imageFolder + thisFile)


# In[35]:


time.sleep(startPause)

i = 0
while True:
    thisPath = imageFolder + "image%s.png" % str(i)
    rectangleParam = "-R%s,%s,%s,%s" % (str(upperCornerX), str(upperCornerY), str(lowerCornerX), str(lowerCornerY))
    call(["screencapture", rectangleParam, thisPath])
    if i > 0:
        newImage = Image.open(thisPath)
        if newImage == oldImage:
            print("Done scanning Kindle book!")
            break
        else:
            oldImage = newImage
    else:
        oldImage = Image.open(thisPath)
    pyautogui.click(clickX, clickY)
    i = i + 1


# In[ ]:




