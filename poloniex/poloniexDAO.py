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
				self.__createTables()
				self.update()


			except sqlite3.Error as detail:

				print "Unable to open db file: ", self.db_path, detail
				raise

		else:
				raise IOError('Directory not found: ' + directory)

	def selectMaxTime(self):
		self.__createTables()
		SQL_MIN = "SELECT max(date) FROM PRICE_1MIN"
		self.__cursor.execute( SQL_MIN )
		return self.__cursor.fetchall()[0][0]

	def selectMinTime(self):
		self.__createTables()
		SQL_MIN = "SELECT min(date) FROM PRICE_1MIN"
		self.__cursor.execute( SQL_MIN )
		return self.__cursor.fetchall()[0][0]

	def selectAllTradeHistory(self):
		self.__createTables()
		SQL_SELECT_ALL = 'SELECT * FROM TRADES ORDER BY tradeID'
		self.__cursor.execute( SQL_SELECT_ALL )
		all_rows = self.__cursor.fetchall()
		return all_rows

	def selectAllPrice1MinHistory(self):
		self.__createTables()
		SQL_SELECT_ALL = 'SELECT * FROM PRICE_1MIN ORDER BY date'
		self.__cursor.execute( SQL_SELECT_ALL )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["date", "open", "high", "low", "close", "volume"]  )

	def selectPrice1MinHistory(self, startTime, endTime):
	
		self.__createTables()
		if type(startTime) == str:
        	startTime = int(time.mktime(time.strptime(startTime, "%Y-%m-%d %H:%M:%S")))
        
    	if type(endTime) == str:
        	endTime = int(time.mktime(time.strptime(endTime, "%Y-%m-%d %H:%M:%S")))

		SQL_SELECT = 'SELECT * FROM PRICE_1MIN WHERE date BETWEEN ? AND ?'
		self.__cursor.execute( SQL_SELECT, [startTime, endTime] )
		all_rows = self.__cursor.fetchall()
		return pandas.DataFrame( all_rows, columns=["date", "open", "high", "low", "close", "volume"]  )

	def clear(self):
		DROP_TRADES_TABLE = "DROP TABLE IF EXISTS TRADES"
		DROP_PRICE_1MIN_TABLE = "DROP TABLE IF EXISTS PRICE_1MIN"
		self.__cursor.execute( DROP_TRADES_TABLE )
		self.__cursor.execute( DROP_PRICE_1MIN_TABLE )


	def update(self):

		s = self.selectMaxTime()
		if(s == None):
			s = int(time.mktime(time.strptime('2016-07-29 21:00:00', "%Y-%m-%d %H:%M:%S")))
		results = poloniexClient.pullTradeHistory(s , int(time.time()), self.currencyPair)
		self.__updateTrades(results)
		self.__updatePrice1Min(results)


	def __createTables(self):
		CREATE_TRADES_TABLE = 'CREATE TABLE IF NOT EXISTS TRADES ("amount" DOUBLE NOT NULL , "date" DATETIME NOT NULL , "globalTradeID" INTEGER PRIMARY KEY  NOT NULL  UNIQUE , "rate" DOUBLE NOT NULL , "total" DOUBLE NOT NULL , "tradeID" INTEGER NOT NULL  UNIQUE , "type" BOOL NOT NULL )'
		CREATE_PRICE_1MIN_TABLE = 'CREATE TABLE IF NOT EXISTS PRICE_1MIN ("date" INT PRIMARY KEY NOT NULL UNIQUE, "open" DOUBLE NOT NULL , "high" DOUBLE NOT NULL , "low" DOUBLE NOT NULL, "close" DOUBLE NOT NULL , "volume" DOUBLE NOT NULL)'
		self.__cursor.execute( CREATE_TRADES_TABLE )
		self.__cursor.execute( CREATE_PRICE_1MIN_TABLE )

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
	 
				SQL_INSERT = " INSERT OR REPLACE INTO TRADES VALUES ( ?, ?, ?, ?, ?, ?,? ) "
				self.__cursor.execute( SQL_INSERT, [amount, date, globalTradeID, rate, total, tradeID, tradeType])

			except sqlite3.Error as detail:
				print( detail , " ", SQL_INSERT)
				pass

	def __updatePrice1Min(self, trades):

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

			price1Min = pandas.concat([price,volume], axis=1)
			price1Min = price1Min.interpolate()
			print price1Min

			for index, row in price1Min.iterrows():
				timeInt = int(time.mktime(time.strptime(str(index), "%Y-%m-%d %H:%M:%S")))
				SQL_INSERT = " INSERT OR REPLACE INTO PRICE_1Min VALUES ( ?, ?, ?, ?, ?, ? ) "
				self.__cursor.execute( SQL_INSERT, [ timeInt, row['open'], row['high'], row['low'], row['close'], row['amount']])


	def close(self):
		self.__conn.commit()
		self.__conn.close()

	def abort(self):
		self.__conn.close()


dao = PoloniexDAO("/Users/JRS/Data/", "BTC_ETH")
dao.update()
print dao.selectMaxTime()
# dao.update('2016-07-20 00:55:00', '2016-07-30 01:00:00')
# print dao.selectAllPrice1MinHistory()
print dao.selectPrice1MinHistory('2016-07-30 04:00:00','2016-07-30 05:00:00' )
dao.close()







