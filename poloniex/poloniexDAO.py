import sqlite3
import poloniex as polo
import os.path
import datetime



class PoloniexDAO():

	def __init__(self, directory, currencyPair):
		if os.path.isdir( directory ):

			self.db_path = directory + currencyPair
			self.currencyPair = currencyPair
			try:
				self.conn = sqlite3.connect( self.db_path )
				self.cursor = self.conn.cursor()
				self.createTables()


			except sqlite3.Error as detail:

				print "Unable to open db file: ", self.db_path, detail
				raise

		else:
				raise IOError('Directory not found: ' + directory)


	def selectAllTradeHistory(self):
		self.createTables()
		SQL_SELECT_ALL = 'SELECT * FROM TRADES'
		self.cursor.execute( SQL_SELECT_ALL )
		all_rows = self.cursor.fetchall()
		return all_rows

	def createTables(self):
		CREATE_TRADES_TABLE = 'CREATE TABLE IF NOT EXISTS TRADES ("amount" DOUBLE NOT NULL , "date" DATETIME NOT NULL , "globalTradeID" INTEGER PRIMARY KEY  NOT NULL  UNIQUE , "rate" DOUBLE NOT NULL , "total" DOUBLE NOT NULL , "tradeID" INTEGER NOT NULL  UNIQUE , "type" BOOL NOT NULL )'
		self.cursor.execute( CREATE_TRADES_TABLE )

	def clear(self):
		DROP_TRADES_TABLE = "DROP TABLE IF EXISTS TRADES"
		self.cursor.execute( DROP_TRADES_TABLE )

	def update(self, startDate, endDate):
		self.createTables()
		results = polo.pullTradeHistory(startDate,endDate, self.currencyPair)
		for trade in results:
			self.insertTrade(trade)	

	def insertTrade(self, trade):
    
		amount        = 	float( trade['amount'] )
		date          = 	str( trade['date'] )
		globalTradeID = 	int( trade['globalTradeID'] )
		rate          = 	float( trade['rate'] )
		total         = 	float( trade['total'] )
		tradeID       = 	int( trade['tradeID'] )
		tradeType     = 	1 if trade['type'] == 'buy' else 0

		try:
 
			SQL_INSERT = " INSERT INTO TRADES VALUES ( ?, ?, ?, ?, ?, ?,? ) "
			self.cursor.execute( SQL_INSERT, [amount, date, globalTradeID, rate, total, tradeID, tradeType])

		except sqlite3.Error as detail:
			print( detail , " ", SQL_INSERT)
			pass

	def close(self):
		self.conn.commit()
		self.conn.close()

	def abort(self):
		self.conn.close()


dao = PoloniexDAO("/Users/JRS/Data/", "BTC_ETH")
dao.clear()
dao.update('2016-07-28 00:00:00', '2016-07-28 01:00:00')
print selectAllTradeHistory()
dao.close()







