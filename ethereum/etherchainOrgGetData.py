#%% PARSE ETHEREUM BLOCK FROM ETHERCHAIN.ORG WEBSITE

import urllib2

#%%

def getURL(url):
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    con = urllib2.urlopen( req )
    dataString = con.read().replace("null","None")
    dataDict = eval(dataString)
    return dataDict
    
#%% get all ethereum transactions in a block
blockID = '1093465'
urlTransactions = 'https://etherchain.org/api/block/' + blockID + '/tx'
transactionDict = getURL(urlTransactions)

# get block info
urlBlock = 'https://etherchain.org/api/block/' + blockID
blockDict = getURL(urlBlock)

# get transactions for an account
accountNumber = '0x63c42389629c3c9dd86ff36fc53d1688ab852a69'
urlTransactionsByAccount = 'https://etherchain.org/api/account/0xf998928c5db3be0eda105c3f9e998b369c896bb2/tx/0'
transByAccountDict = getURL(urlTransactionsByAccount)

#%% get most recent transactions

offset = 0
count = 1000
urlTransactionsRecent = 'https://etherchain.org/api/txs/%s/%s' % (offset,count)
transactionRecentDict = getURL(urlTransactionsAlt)

set([i['isContractTx'] for i in transactionRecentDict['data']])