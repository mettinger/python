#!/Users/marke/anaconda/bin/python

import numpy as np
import datetime

meditations = ['ground in sensation', 'reality checks', 'simulation yoga/epoche','push/pull','sense of being','ego motivation','acceptance']
print str(datetime.date.today()) + ": "  + np.random.choice(meditations)
