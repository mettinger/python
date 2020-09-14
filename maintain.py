# auto move and click

import pyautogui
import time
import random

xLim,yLim = pyautogui.size()

avgMinutesSleep = 7

while True:
    newX = xLim/2 + random.randint(0,50)
    newY = yLim/2 + random.randint(0,60)
    pyautogui.moveTo(newX, newY, duration = .5)
    pyautogui.dragTo(newX, newY, duration = .5, button='left') 
    secondsToSleep = (60 * avgMinutesSleep) + random.randint(3, 60)
    time.sleep(secondsToSleep)