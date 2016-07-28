#%%

import urllib
import urllib2
import json
import time
import hmac,hashlib
import sqlite3
import time
import config


def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return int(time.mktime(time.strptime(datestr, format)))

class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            if 'start' in req:
                requestString = 'https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair']) + '&start=' + str(req['start']) + '&end=' + str(req['end'])
                ret = urllib2.urlopen(urllib2.Request(requestString))
            else:
                ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})
    
    # Rolls out trade history starting at startHour and endhour by performing consecutive pull requests         
    # Inputs:
    # startHour     The begining date
    # endHour       The ending date 
    # currencyPair  The currency to withdrawl
    # Outputs: 
    # response      A dictionary containing the trade history
def hourlyDataPull(startHour, endHour, currencyPair = 'BTC_ETH'):
    dataDict = {}
    poloniexAPI = poloniex('', '')
    i = 0
    for thisStart in range(startHour, endHour, 3600):
        if i % 24 == 0:
            print "begin day: " + str(i / 24)
        req = {'currencyPair': currencyPair, 'start': thisStart, 'end': thisStart + 3599}
        dataDict[thisStart] = poloniexAPI.api_query('returnMarketTradeHistory',req)
        time.sleep(.25)
        i += 1
    return dataDict
    
def sqliteInsert(cursor, thisTrade):
    
    amount = float(thisTrade['amount'])
    date = str(thisTrade['date'])
    globalTradeID = int(thisTrade['globalTradeID'])
    rate = float(thisTrade['rate'])
    total = float(thisTrade['total'])
    tradeID = int(thisTrade['tradeID'])
    tradeType = 1 if thisTrade['type'] == 'buy' else 0
    try:
        queryString = "INSERT INTO trades ('amount', 'date', 'globalTradeID', 'rate', 'total', 'tradeID', 'type') \
                        VALUES (%s,'%s',%s,%s,%s,%s,%s)" % \
                        (amount, date, globalTradeID, rate, total, tradeID, tradeType)
        cursor.execute(queryString)
    except:
        print('Insert error: ' + queryString)
        pass
    

def hourlyDataPullDB(startHour, endHour, sqliteFile, currencyPair = 'BTC_ETH'):
    poloniexAPI = poloniex('', '')
    i = 0
    conn = sqlite3.connect(sqliteFile)
    cursor = conn.cursor()
    for thisStart in range(startHour, endHour, 3600):
        if i % 24 == 0:
            print "begin day: " + str(i / 24)
        req = {'currencyPair': currencyPair, 'start': thisStart, 'end': thisStart + 3599}
        queryResult = poloniexAPI.api_query('returnMarketTradeHistory',req)
        for thisTrade in queryResult:
            sqliteInsert(cursor, thisTrade)
        conn.commit()
        time.sleep(.25)
        i += 1
    
    conn.close()
    

#%%

startHour = createTimeStamp('2016-07-20 00:00:00')
endHour = createTimeStamp('2016-07-26 00:00:00')
sqliteFile = '/Users/mark/Data/poloniexBTC_ETH.sqlite'

#hourlyData = hourlyDataPull(startHour, endHour)
hourlyDataPullDB(startHour, endHour, sqliteFile)

#%%

# Add APIkey and Secret to "config.py"     
APIKey = config.poloniex_key
Secret = config.poloniex_secret

poloniexAPI = poloniex(APIKey, Secret)
start = createTimeStamp('2015-08-07 00:00:00')
end = createTimeStamp('2015-08-08 00:00:00')
req = {'currencyPair':'BTC_ETH', 'start': start, 'end': end}
history = poloniexAPI.api_query('returnMarketTradeHistory',req)

# test



    











