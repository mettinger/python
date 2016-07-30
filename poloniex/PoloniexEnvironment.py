"""
.. Authors: Mark Ettinger & Jacob Steeves
"""
import numpy as np
from deer.base_classes import Environment
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import theano
import copy

import poloniex as pol
import pandas as pd


def loadSeries():
	startHourString = '2016-07-28 00:00:00'
	endHourString = '2016-07-28 23:00:00'
	data = pol.pullTradeHistory(startHourString, endHourString) 
	history = pd.DataFrame(data)
	history = history.apply(lambda x: pd.to_numeric(x, errors='ignore')) 
	history['date'] = pd.to_datetime(history['date'], unit='s')
	price = history[['date','rate']]
	price = price.groupby('date')['rate'].mean()
	price = price.resample('1Min', how='ohlc')
	return price['close'].values.tolist()

class PoloniexEnvironment( Environment ): 




	def __init__( self ):
		
		""" Initialize environment.
        """
       
		self.prices_full = loadSeries() ### insert poloniex timeseries here

		print " Price history has " , len(self.prices_full), " examples"

		self.prices_train = self.prices_full[ :len(self.prices_full)//2 ]
		self.prices_valid = self.prices_full[ len(self.prices_full)//2: ]
		self.prices  = None
		self.counter = 1
		self.holding = 0
		self.observation = [ 0, self.holding ]


	def reset( self, mode ):
		"""Reset the environment and put it in mode [mode].
        
		The [mode] can be used to discriminate for instance between an agent which is training or trying to get a 
		validation or generalization score. The mode the environment is in should always be redefined by resetting the
		environment using this method, meaning that the mode should be preserved until the next call to reset().

		Parameters
		-----------
		mode : int 
			The mode to put the environment into. Mode "-1" is reserved and always means "training".
        """
		if mode == -1:
			self.prices = self.prices_train
		else:
			self.prices = self.prices_valid

		self.holding = 0
		self.counter = 1
		self.observation = [ self.prices[ self.counter ], self.holding ]
		return [[0, 0, 0, 0, 0, 0], 0]
     

	def act( self, action ):
		"""Apply the agent action [action] on the environment.

        Parameters
        -----------
        action : int
            The action selected by the agent to operate on the environment. Should be an identifier 
            included between 0 included and nActions() excluded.
		"""
		reward = 0
		asset_price = self.prices[ self.counter - 1 ] 
		if (action == 0 and self.holding == 1):
			reward =  asset_price - asset_price*0.01
			#reward =  asset_price
			self.holding = 0

		if (action == 1 and self.holding == 0):
			reward = - asset_price - asset_price*0.01
			#reward = asset_price
			self.holding = 1

		self.observation = [ self.prices[ self.counter ], self.holding ]
		self.counter += 1

		return reward

	def inputDimensions( self ):
		"""Get the shape of the input space for this environment.
        
		This returns a list whose length is the number of subjects observed on the environment. Each element of the 
		list is a tuple whose content and size depends on the type of data observed: the first integer is always the 
		history size (or batch size) for observing this subject and the rest describes the shape of a single 
		observation on this subject:
		- () or (1,) means each observation on this subject is a single number and the history size is 1 (= no history)
		- (N,) means each observation on this subject is a single number and the history size is N
		- (N, M) means each observation on this subject is a vector of length M  and the history size is N
		- (N, M1, M2) means each observation on this subject is a matrix with M1 rows and M2 columns and the history 
		size is N
		"""

		return [(6,), (1,)]


	def nActions( self ):
		"""Get the number of different actions that can be taken on this environment."""

		return 2

	def inTerminalState( self ):
		"""Tell whether the environment reached a terminal state after the last transition (i.e. the last transition 
		that occured was terminal).

		As the majority of control tasks considered have no end (a continuous control should be operated), by default 
		this returns always False. But in the context of a video game for instance, terminal states can occurs and 
		these cases this method should be overriden.
        
		Returns
		-------
		isTerminal : bool

		"""

		if( self.counter >= len(self.prices)):
			return True
		else:
			return False

	def observe( self ):
		"""Get a list of punctual observations on all subjects composing this environment.
        
		This returns a list where element i is a punctual observation on subject i. You will notice that the history 
		of observations on this subject is not returned; only the very last observation. Each element is thus either 
		a number, vector or matrix and not a succession of numbers, vectors and matrices.

		See the documentation of batchDimensions() for more information about the shape of the observations according 
		to their mathematical representation (number, vector or matrix).
		"""

	
		return np.array( self.observation )

	def summarizePerformance( self, test_data_set ):
		"""Optional hook that can be used to show a summary of the performance of the agent on the
		environment in the current mode.

		Parameters
		-----------
		test_data_set : agent.DataSet 
			The dataset maintained by the agent in the current mode, which contains 
			observations, actions taken and rewards obtained, as well as wether each transition was terminal or 
			not. Refer to the documentation of agent.DataSet for more information.
		"""
		print ("Summary Perf")
        
		observations = test_data_set.observations()
		prices = observations[0][:]
		invest = observations[1][:]
        
		steps=np.arange(len(prices))
		steps_long=np.arange(len(prices)*10)/10.
        
        #print steps,invest,prices
		host = host_subplot(111, axes_class=AA.Axes)
		plt.subplots_adjust(right=0.9, left=0.1)
    
		par1 = host.twinx()
    
		host.set_xlabel("Time")
		host.set_ylabel("Price")
		par1.set_ylabel("Investment")
    
		p1, = host.plot(steps_long, np.repeat(prices,10), lw=3, c = 'b', alpha=0.8, ls='-', label = 'Price')
		p2, = par1.plot(steps, invest, marker='o', lw=3, c = 'g', alpha=0.5, ls='-', label = 'Investment')

		par1.set_ylim(-0.09, 1.09)
    
    
		host.axis["left"].label.set_color(p1.get_color())
		par1.axis["right"].label.set_color(p2.get_color())
    
		plt.savefig("plot.png")
		print ("A plot of the policy obtained has been saved under the name plot.png")

	def observationType(self, subject):
		"""Get the most inner type (np.uint8, np.float32, ...) of [subject].

		Parameters
		-----------
		subject : int
			The subject
		"""

		return np.float32

	def end(self):
		"""Optional hook called at the end of all epochs
		"""

		pass


def main():

    # Can be used for debug purposes
    env = PoloniexEnvironment()

    print (env.observe())
    
if __name__ == "__main__":
    main()
