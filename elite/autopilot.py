from concurrent.futures.process import _threads_wakeups
import pyautogui
import keyboard
import numpy as np
import time
import json
import os

# TODO: search for fuel-scoop-finished image, autofind of current log file, lose circle -refind circle

pyautogui.PAUSE = 2.5
pyautogui.FAILSAFE = True
screenX, screenY = pyautogui.size() # resolution
pitchSecondsPerCycle = 21   # number of seconds to complete a pitch rotation at speed = 0
yawSecondsPerCycle = 83     # seconds to complete a yaw rotation at speed = 0
circleCenterPixelX = 54     # x offset of circle center in image
circleCenterPixelY = 64     # y offset of circle center in image
imageX, imageY = 77,129     # dimensions of circle image
circleTolerance = 20        # tolerance of movement to get close to circle center
centerCirclePitchSeconds = .2  # seconds for each pitch step when centering the circle
centerCircleYawSeconds = .2    # seconds for each yaw step when centering the circle
fuelForwardSeconds = 4.0       # seconds to move forward toward star to fuel scoop
fuelWaitSeconds = 20           # seconds to wait while fuel scooping
logDirectory = "C:/Users/the_m/Saved Games/Frontier Developments/Elite Dangerous/"

runAwaySeconds = 20
preRunAwayPitchAngle = pitchSecondsPerCycle * (1/4)
postRunAwayPitchAngle = pitchSecondsPerCycle * (1/4)
circleFindPitchIncrement = -2 * np.pi/360
circleFindYawIncrement = 2 * np.pi/725

## IMPORTANT ##
killOnEmergency = False
checkEmergencyFlag = False
fuelEmergencyAmmount = 10
logFile = 'Journal.2022-08-06T041841.01.log'


def keyPress(keyString, midDelay, endDelay):
    keyboard.press(keyString)
    time.sleep(midDelay)
    keyboard.release(keyString)
    time.sleep(endDelay)
    return

def stopShip():
    keyPress('x', .1, .1)
    return

def forwardShip(seconds):
    keyPress('w', seconds, .1)
    return

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

def hyperjump():
    keyPress('j', .1, 0)
    keyPress('w', 5, 0)
    print("hyperjump completed...")

def shipWindowColorGet():
    x = 600
    y = 0
    width = 700
    height = 700

    im = pyautogui.screenshot(region=(x, y, width, height))
    average_color_row = np.average(im, axis=0)
    average_color = np.average(average_color_row, axis=0)
    return average_color

def runAwayFromStar():

    stopShip()
    forwardShip(fuelForwardSeconds)
    stopShip()
    time.sleep(fuelWaitSeconds)

    keyPress('i', preRunAwayPitchAngle, .1) # pitch up to get away from star
    keyboard.press(']') # honk the system
    forwardShip(runAwaySeconds) # run away from star
    keyboard.release(']')
    stopShip()
    keyPress('k', postRunAwayPitchAngle, .1) # pitch down to begin looking for target circle
    print("run away complete")

# find the target circle on the screen
def targetCircleFind():

    while True:
        circle = pyautogui.locateOnScreen('target2.png', confidence=0.5)
        if circle != None:
            left, top, width, height = circle
            print("circle target found: ")
            print(left,top,width,height)
            return (left, top, width, height)
        else:
            pitchTheta(circleFindPitchIncrement)
            yawPhi(circleFindYawIncrement)


# center the target circle for next jump
def centerCircle():

    while True:
        x, y, _, _ = pyautogui.locateOnScreen('target2.png', confidence=0.5)
        currentCenterX = x + circleCenterPixelX
        currentCenterY = y + circleCenterPixelY

        if currentCenterX < screenX/2 - circleTolerance:
            keyPress('a', centerCircleYawSeconds, .1)
        elif currentCenterX > screenX/2. + circleTolerance:
            keyPress('d',centerCircleYawSeconds, .1)
        else:
            keyboard.release('a')
            keyboard.release('d')

        if currentCenterY < screenY/2 - circleTolerance:
            keyPress('i', centerCirclePitchSeconds, .1)
        elif currentCenterY > screenY/2. + circleTolerance:
            keyPress('k', centerCirclePitchSeconds, .1)
        else:
            keyboard.release('i')
            keyboard.release('k')

        if (abs(currentCenterX - (screenX/2.)) <= circleTolerance) and (abs(currentCenterY - (screenY/2)) <= circleTolerance):
            print("centering completed...")
            return
        
def checkFuel():
  
    f = open('C:/Users/the_m/Saved Games/Frontier Developments/Elite Dangerous/Status.json','r')
    statusData = json.load(f)
    f.close()
    fuelAmount = statusData['Fuel']['FuelMain']

    if fuelAmount < fuelEmergencyAmmount:
        return True
    else:
        return False

def checkEmergency():
    
    if not checkEmergencyFlag:
        return False

    eventList = []
    with open(logDirectory + logFile, 'r') as myfile:
        lines = myfile.readlines()
        for thisLine in lines:
            thisDict = json.loads(thisLine)
            eventList.append(thisDict['event'])

    uniqueEvents = list(set(eventList))

    emergencyEventList = ['SupercruiseExit', 'HeatDamage', 'HullDamage']
    for event in emergencyEventList:
        if event in uniqueEvents:
            print("Emergency: %s" % event)
            return True

    print("No Emergency...")
    return False

def autoJump():
    print("entering autojump")
    while True:
        try:
            if keyboard.is_pressed('-'):
                print("autojump canceled...")
                return False

            avgColor = shipWindowColorGet()
            colorNorm = np.linalg.norm(avgColor)

            if colorNorm >= 170:
                print("starting tactic...")
                runAwayFromStar()
                if checkFuel():
                    print("fuel low.  exiting game...")
                    return True
                if checkEmergency():
                    print("Emergency after runaway...")
                    return True
                targetCircleFind()
                if checkEmergency():
                    print("Emergency after circle find...")
                    return True
                centerCircle()
                if checkEmergency():
                    print("Emergency after center circle...")
                    return True
                hyperjump()
                if checkEmergency():
                    print("Emergency after hyperjump...")
                    return True
                print("ending tactic...")
        except Exception as e: 
            print('Strange error in autojump...')
            print(e)
            return True 

while True:
    if keyboard.is_pressed('='):
        print('exit')
        break
    if keyboard.is_pressed('0'):
        try:
            emergencyFlag = autoJump()
        except:
            emergencyFlag = True

        if emergencyFlag:
            stopShip()
            if killOnEmergency:
                os.system("taskkill /im EliteDangerous64.exe")
            break 
    if keyboard.is_pressed('6'):
        avgColor = shipWindowColorGet()
        colorNorm = np.linalg.norm(avgColor)
        print(avgColor)
        print(colorNorm)

'''
runAwaySeconds = 20
preRunAwayPitchAngle = pitchSecondsPerCycle/4
postRunAwayPitchAngle = pitchSecondsPerCycle/2
circleFindPitchIncrement = 2 * np.pi/100
circleFindYawIncrement = 2 * np.pi/180
'''