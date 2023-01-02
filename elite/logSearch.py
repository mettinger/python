#%%
import json
import os
# %%

directory = "C:/Users/the_m/Saved Games/Frontier Developments/Elite Dangerous/"
files = os.listdir(directory)
journals = [i for i in files if i.startswith('Journal') and i.endswith('.log') and '-08-' in i]

# %%

eventList = []
allEntries = []

for i in journals:
    with open(directory + i, 'r') as myfile:
        lines = myfile.readlines()
        for thisLine in lines:
            thisDict = json.loads(thisLine)
            allEntries.append(thisDict)
            eventList.append(thisDict['event'])

uniqueEvents = list(set(eventList))
print(len(uniqueEvents))
uniqueEvents
# %%
[i for i in allEntries if i['event'] == 'HullDamage']


# %%
import os

# SupercruiseExit  HeatWarning ( also HeatDamage HullDamage)

#os.system("taskkill /f /pid 23248")
os.system("taskkill /im EliteDangerous64.exe")
# %%
import os
import glob

logDirectory = "C:/Users/the_m/Saved Games/Frontier Developments/Elite Dangerous/"
list_of_files = glob.glob(logDirectory + '*.log')
logFile = max(list_of_files, key=os.path.getctime)
print(logFile)

# %%
