#%% PARSE ETHEREUM BLOCK FROM ETHERCHAIN.ORG WEBSITE

import urllib2

#%% get all ethereum transactions in a block

url = 'https://etherchain.org/api/block/1039153/tx'

req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
con = urllib2.urlopen( req )
dataString = con.read().replace("null","None")
dataDict = eval(dataString)