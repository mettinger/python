import pyautogui
import keyboard
import cv2
import numpy as np
import time
import math

pyautogui.PAUSE = 2.5
pyautogui.FAILSAFE = True
xPix, yPix = pyautogui.size()
pitchSecondsPerCycle = 21
yawSecondsPerCycle = 83
circleCenterPixelX = 54
circleCenterPixelY = 64
imageX, imageY = 77,129
screenX, screenY = 1920, 1080
circleTolerance = 20
runAwaySeconds = 20

def shipWindowColorGet():
    x = 600
    y = 0
    width = 700
    height = 700

    im = pyautogui.screenshot(region=(x, y, width, height))
    average_color_row = np.average(im, axis=0)
    average_color = np.average(average_color_row, axis=0)
    return average_color

def keyPress(keyString, midDelay, endDelay):
    keyboard.press(keyString)
    time.sleep(midDelay)
    keyboard.release(keyString)
    time.sleep(endDelay)
    return

def stop():
    keyPress('x', .1, .1)
    return

def forward(seconds):
    keyPress('w', seconds, .1)
    return

def runAwayFromStar():
    pitchAngle0 = pitchSecondsPerCycle/4
    pitchAngle1 = pitchSecondsPerCycle/2
    fuelForwardSeconds = 4.0
    fuelWaitSeconds = 30

    stop()
    keyPress('w', fuelForwardSeconds, .1)
    stop()
    time.sleep(fuelWaitSeconds)

    keyPress('i', pitchAngle0, .1)
    keyboard.press(']')
    forward(runAwaySeconds)
    keyboard.release(']')
    stop()
    keyPress('k', pitchAngle1, .1)
    print("run away complete")

def pitchTheta(theta):
    if theta >= 0:
        seconds = pitchSecondsPerCycle * theta
        keyPress('i', seconds, .1)
    else:
        seconds = pitchSecondsPerCycle * -theta
        keyPress('k', seconds, .1)
    return

def yawPhi(phi):
    if phi >= 0:
        seconds = pitchSecondsPerCycle * phi
        keyPress('d', seconds, .1)
    else:
        seconds = pitchSecondsPerCycle * -phi
        keyPress('a', seconds, .1)
    return

def targetCircleFind():
    pitchIncrement = 2 * np.pi/100
    yawIncrement = 2 * np.pi/180

    while True:
        circle = pyautogui.locateOnScreen('target2.png', confidence=0.5)
        if circle != None:
            left, top, width, height = circle
            print("circle target found: ")
            print(left,top,width,height)
            return (left, top, width, height)
        else:
            pitchTheta(pitchIncrement)
            yawPhi(yawIncrement)


def centerCircle():
    pitchSeconds = .2
    yawSeconds = .2

    while True:
        x, y, _, _ = pyautogui.locateOnScreen('target2.png', confidence=0.5)
        currentCenterX = x + circleCenterPixelX
        currentCenterY = y + circleCenterPixelY

        if currentCenterX < screenX/2 - circleTolerance:
            keyPress('a', yawSeconds, .1)
        elif currentCenterX > screenX/2. + circleTolerance:
            keyPress('d',yawSeconds, .1)
        else:
            keyboard.release('a')
            keyboard.release('d')

        if currentCenterY < screenY/2 - circleTolerance:
            keyPress('i', pitchSeconds, .1)
        elif currentCenterY > screenY/2. + circleTolerance:
            keyPress('k', pitchSeconds, .1)
        else:
            keyboard.release('i')
            keyboard.release('k')

        if (abs(currentCenterX - (screenX/2.)) <= circleTolerance) and (abs(currentCenterY - (screenY/2)) <= circleTolerance):
            print("centering completed...")
            return
        

def hyperjump():
    keyPress('j', .1, 0)
    keyPress('w', 5, 0)
    print("hyperjump completed...")

def autoJump():
    print("entering autojump")
    while True:
        if keyboard.is_pressed('-'):
            print("autojump canceled...")
            return

        avgColor = shipWindowColorGet()
        colorNorm = np.linalg.norm(avgColor)

        if colorNorm >= 170:
            print("starting tactic...")
            runAwayFromStar()
            targetCircleFind()
            centerCircle()
            hyperjump()
            print("ending tactic...")

while True:
    if keyboard.is_pressed('='):
        print('exit')
        break
    if keyboard.is_pressed('0'):
        autoJump()
    if keyboard.is_pressed('6'):
        avgColor = shipWindowColorGet()
        colorNorm = np.linalg.norm(avgColor)
        print(avgColor)
        print(colorNorm)

    
    
'''
def runAwayFromStar():
    normBound = 7

    stop()

    avgColor = shipWindowColorGet()
    colorNorm = np.linalg.norm(avgColor)
    if colorNorm >= normBound:
        pitchPi()
        forward(runAwaySeconds)
        stop()
        print("run away complete")


def centerCircle():
    while True:
        x, y, _, _ = pyautogui.locateOnScreen('target2.png', confidence=0.5)
        currentCenterX = x + circleCenterPixelX
        currentCenterY = y + circleCenterPixelY
        if (abs(currentCenterX - (screenX/2.)) <= circleTolerance) and (abs(currentCenterY - (screenY/2)) <= circleTolerance):
            print("centering completed...")
            break
        else:
            radiusPitch = 2 ** 13
            radiusYaw = 2 ** 11

            pitchIncrement = math.atan2(((screenY/2) - currentCenterY), radiusPitch)
            pitchTheta(pitchIncrement)

            yawIncrement = math.atan2((currentCenterX - (screenX/2)), radiusYaw)
            yawPhi(yawIncrement)
'''
