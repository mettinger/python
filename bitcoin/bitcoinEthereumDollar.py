#%% GET DATA FROM POLONIEX AND KRAKEN

import matplotlib
matplotlib.style .use( 'ggplot' ) 

import time
import datetime
import urllib2

#%% 

def getURL(url):
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    con = urllib2.urlopen( req )
    dataString = con.read().replace("null","None")
    return eval(dataString)

#%% TICKER

'''
KRAKEN INFO

<pair_name> = pair name
    a = ask array(<price>, <whole lot volume>, <lot volume>),
    b = bid array(<price>, <whole lot volume>, <lot volume>),
    c = last trade closed array(<price>, <lot volume>),
    v = volume array(<today>, <last 24 hours>),
    p = volume weighted average price array(<today>, <last 24 hours>),
    t = number of trades array(<today>, <last 24 hours>),
    l = low array(<today>, <last 24 hours>),
    h = high array(<today>, <last 24 hours>),
    o = today's opening price
'''

def krakenTickerETH():
    urlETH = 'https://api.kraken.com/0/public/Ticker?pair=ETHUSD'
    data = getURL(urlETH)
    return data

def krakenTickerBTC():
    urlBTC = 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD'
    data = getURL(urlBTC)
    return data

def poloniexTicker():
    url = 'https://poloniex.com/public?command=returnTicker'
    data = getURL(url)
    return data

def poloniexOrderBook():
    url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=USDT_BTC&depth=50'
    data = getURL(url)
    return data
    
def krakenOrderBook():
    url = 'https://api.kraken.com/0/public/Depth?pair=XBTUSD'
    data = getURL(url)
    return data
    
def bitcoinPriceSpreads():
    krakenData = krakenOrderBook()['result']['XXBTZUSD']
    krakenBids = krakenData['bids']
    kradenAsks = krakenData['asks']
    poloniexData = poloniexOrderBook()
    poloniexBids = poloniexData['bids']
    poloniexAsks = poloniexData['asks']
    spread1 = float(krakenBids[0][0]) - float(poloniexAsks[0][0])
    spread2 = float(poloniexBids[0][0]) - float(kradenAsks[0][0])
    return (spread1,spread2)
    
        
def bitcoinPriceDiffLastOrder():
    krakenData = krakenTickerBTC()
    poloniexData = poloniexTicker()
    krakenPrice = float(krakenData['result']['XXBTZUSD']['c'][0])
    poloniexPrice = float(poloniexData['USDT_BTC']['last'])
    diff = krakenPrice - poloniexPrice
    return (diff, krakenPrice, poloniexPrice)
    
    

bitcoinPriceSpreads()

#%%

startDate = "01/01/2016"
endDate = "25/02/2016"

startEpoch = int(time.mktime(datetime.datetime.strptime(startDate, "%d/%m/%Y").timetuple()))
endEpoch = int(time.mktime(datetime.datetime.strptime(endDate, "%d/%m/%Y").timetuple()))

#%% POLONIEX

urlBTC = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair=USDT_BTC&start=%s&end=%s' % (startEpoch, endEpoch)
urlETH = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair=USDT_ETH&start=%s&end=%s' % (startEpoch, endEpoch)

req = urllib2.Request(urlBTC, headers={'User-Agent' : "Magic Browser"}) 
con = urllib2.urlopen( req )
dataString = con.read().replace("null","None")
dataDictBTC = eval(dataString)

req = urllib2.Request(urlETH, headers={'User-Agent' : "Magic Browser"}) 
con = urllib2.urlopen( req )
dataString = con.read().replace("null","None")
dataDictETH = eval(dataString)


    
    
    





