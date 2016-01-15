#%% DOWNLOAD AND PREPROCESS DATA

import pandas as pd
import sys
import requests, zipfile, StringIO

#%% get command line arguments: zipfile URL and number of samples
'''
if len(sys.argv) < 2:
    print "data set URL required...exiting...."
    sys.exit()
else:
    zipFileURL = sys.argv[1]
    numSample = int(sys.argv[2])
  '''  
#%% download the data
    
zipFileURL = 'https://resources.lendingclub.com/LoanStats3b.csv.zip'
r = requests.get(zipFileURL)
z = zipfile.ZipFile(StringIO.StringIO(r.content))

#%% read the data

csvFile = zipFileURL.split('/')[-1][0:-4]
df = pd.read_csv(z.open(csvFile), skiprows=1)

#%% reduce the data

dfSmall = df.sample(numSample)[['id','loan_status']]

#%% save the reduced data

sampleFile = 'random.csv'
dfSmall.to_csv(sampleFile, index = False)

#%% print the size of the file

print "Number of random samples in " + sampleFile + ": " + str(numSample)