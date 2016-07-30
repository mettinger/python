import sqlite3
import poloniexClient
import os.path
import datetime
import pandas
import time
import datetime
import math


class PoloniexDAO():

	def __init__(self, directory, currencyPair):
		if os.path.isdir( directory ):

			self.db_path = directory + currencyPair
			self.currencyPair = currencyPair
			try:
				self.__conn = sqlite3.connect( self.db_path )
				self.__cursor = self.__conn.cursor()
				self.createTables()


			except sqlite3.Error as detail:

				print "Unable to open db file: ", self.db_path, detail
				raise

		else:
				raise IOError('Directory not found: ' + directory)

	def selectMaxTime(self):
		self.createTables()
		SQL_MIN = "SELECT max(date) FROM PRICE"
		self.__cursor.execute( SQL_MIN )
		return self.__cursor.fetchall()[0][0]

	def selectMinTime(self):
		self.createTables()
		SQL_MIN = "SELECT min(date) FROM PRICE"
		self.__cursor.execute( SQL_MIN )
		return self.__cursor.fetchall()[0][0]

	def selectAllTradeHistory(self):
		self.createTables()
		SQL_SELECT_ALL = 'SELECT * FROM TRADES ORDER BY tradeID'
		self.__cursor.execute( SQL_SELECT_ALL )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["amount", "date", "globaleTradeID", "rate", "total", "tradeID", "type"]  )

	def selectTradeHistory(self, startTime, endTime):
		self.createTables()
		SQL_SELECT_ALL = 'SELECT * FROM TRADES WHERE date BETWEEN ? AND ? ORDER BY tradeID'
		self.__cursor.execute( SQL_SELECT_ALL, [startTime, endTime]  )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["amount", "date", "globaleTradeID", "rate", "total", "tradeID", "type"]  )

	def selectAllPriceHistory(self):
		self.createTables()
		SQL_SELECT_ALL = 'SELECT * FROM PRICE ORDER BY date'
		self.__cursor.execute( SQL_SELECT_ALL )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["date", "open", "high", "low", "close", "volume"]  )

	def selectPriceHistory(self, startTime, endTime):
		self.createTables()
		SQL_SELECT = 'SELECT * FROM PRICE WHERE date BETWEEN ? AND ? ORDER BY date'
		self.__cursor.execute( SQL_SELECT, [startTime, endTime] )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["date", "open", "high", "low", "close", "volume"]  )

	def dropTables(self):
		DROP_TRADES_TABLE = "DROP TABLE IF EXISTS TRADES"
		DROP_PRICE_TABLE = "DROP TABLE IF EXISTS PRICE"
		self.__cursor.execute( DROP_TRADES_TABLE )
		self.__cursor.execute( DROP_PRICE_TABLE )

	def createTables(self):
		CREATE_TRADES_TABLE = 'CREATE TABLE IF NOT EXISTS TRADES ("amount" DOUBLE NOT NULL , "date" DATETIME NOT NULL ,  "globalTradeID" INTEGER PRIMARY KEY  NOT NULL  UNIQUE , "rate" DOUBLE NOT NULL , "total" DOUBLE NOT NULL , "tradeID" INTEGER NOT NULL  UNIQUE , "type" BOOL NOT NULL )'
		CREATE_PRICE_TABLE = 'CREATE TABLE IF NOT EXISTS PRICE ("date" INT PRIMARY KEY NOT NULL UNIQUE, "open" DOUBLE NOT NULL , "high" DOUBLE NOT NULL , "low" DOUBLE NOT NULL, "close" DOUBLE NOT NULL , "volume" DOUBLE NOT NULL)'
		self.__cursor.execute( CREATE_TRADES_TABLE )
		self.__cursor.execute( CREATE_PRICE_TABLE )


	def update(self):

		startTime = self.selectMaxTime()
		endTime = int(time.time())
		if(startTime == None):
			startTime = '2016-07-29 21:00:00'
		startTime = toSeconds(startTime)

		results = self.__pullTradeHistory( startTime, endTime )
		self.__updateTrades(results)
		self.__updatePrice(results)

	def close(self):
		self.__conn.commit()
		self.__conn.close()

	def abort(self):
		self.__conn.close()

	def __pullTradeHistory(self, startTime, endTime):

		history = []
		poloniexAPI = poloniexClient.PoloniexClient('', '')
		i = 0
		for thisStart in range( startTime , endTime, 3600):
			req = {'currencyPair': self.currencyPair, 'start': thisStart, 'end': thisStart + 3599}
			result = poloniexAPI.api_query('returnMarketTradeHistory',req) 
			if( type(result) != list):
				print "Error: ", result
				break
			else:
				history = history + result
			time.sleep(.25)
			i += 1
		return history

	def __updateTrades(self, trades):
		for trade in trades:
			amount        = 	float( trade['amount'] )
			date          = 	str( trade['date'] )
			globalTradeID = 	int( trade['globalTradeID'] )
			rate          = 	float( trade['rate'] )
			total         = 	float( trade['total'] )
			tradeID       = 	int( trade['tradeID'] )
			tradeType     = 	1 if trade['type'] == 'buy' else 0
			try:
				SQL_INSERT = " INSERT OR REPLACE INTO TRADES VALUES ( ?,  ?, ?, ?, ?, ?, ? ) "
				self.__cursor.execute( SQL_INSERT, [amount, date, globalTradeID, rate, total, tradeID, tradeType])

			except sqlite3.Error as detail:
				print( detail , " ", SQL_INSERT)
				pass

	def __updatePrice(self, trades):

		if ( len(trades) > 0 ):
			# Convert to DataFrame 
			history = pandas.DataFrame( trades, columns=["amount", "date", "globalTradeID", "rate", "total", "tradeID", "type"]  )
			# Cast objects to numeric values
			history = history.apply(lambda x: pandas.to_numeric(x, errors='ignore')) 
			# Cast date to datetime 
			history['date'] = pandas.to_datetime(history['date'], unit='s')

			# Price history 
			price = history[['date','rate']]
			# Aggregate simultateous trades 
			price = price.groupby('date')['rate'].mean()
			# Create 1Min candlestick values [close, high, low, open]
			price = price.resample('1Min', how='ohlc')

			# Volume history
			volume = history[['date','amount']]
			# Sum volume of simultaneous trades
			volume = volume.groupby('date')['amount'].sum()
			# Create 1Min volume sums
			volume = volume.resample('1Min', how='sum')

			price = pandas.concat([price,volume], axis=1)
			price['open'] = price['open'].fillna(method='ffill')
			price['high'] = price['high'].fillna(method='ffill')
			price['low'] = price['low'].fillna(method='ffill')
			price['close'] = price['close'].fillna(method='ffill')
			price['amount'] = price['amount'].fillna(0)


			for index, row in price.iterrows():
				SQL_INSERT = " INSERT OR REPLACE INTO PRICE VALUES ( ?, ?, ?, ?, ?, ? ) "
				self.__cursor.execute( SQL_INSERT, [ str(index), row['open'], row['high'], row['low'], row['close'], row['amount']])


def toSeconds(date):
	return int(time.mktime(time.strptime( str(date) , "%Y-%m-%d %H:%M:%S")))





dao = PoloniexDAO("/Users/JRS/Data/", "BTC_XCP")
dao.dropTables()
dao.update()
print dao.selectMaxTime()
print dao.selectMinTime()
print dao.selectAllPriceHistory()
print dao.selectAllTradeHistory()
print dao.selectTradeHistory('2016-07-30 04:09:00','2016-07-30 04:25:00' )
print dao.selectPriceHistory('2016-07-30 04:09:00','2016-07-30 04:25:00' )
dao.close()


dao = PoloniexDAO("/Users/JRS/Data/", "BTC_ETH")
dao.dropTables()
dao.update()
print dao.selectMaxTime()
print dao.selectMinTime()
print dao.selectAllPriceHistory()
print dao.selectAllTradeHistory()
print dao.selectTradeHistory('2016-07-30 04:09:00','2016-07-30 04:25:00' )
print dao.selectPriceHistory('2016-07-30 04:09:00','2016-07-30 04:25:00' )
dao.close()







