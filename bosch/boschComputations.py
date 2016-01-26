#%%

#%matplotlib osx
import math
import scipy.special
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
plt.style.use('ggplot')

#%%

def hoeffdingInverse(t, spread, target):
    return -math.log(target/2.0) * (spread**2)/(2 * t * t)
    
accuracy = .01
spread = 10**4 + 1
probTarget = .99
result = hoeffdingInverse(accuracy,spread,probTarget)

print result

#%%

trueEpsilon = 1./10**4
trials = 3.5 * 10**9
#success = round(trials * trueEpsilon)
success = scipy.stats.binom.rvs(trials,trueEpsilon)
# use uniform beta prior
a = 1 + success
b = 1 + trials - success


rtpLower = .99
rtpUpper = 1.01
prob = scipy.stats.beta.cdf(rtpUpper/10**4,a,b) - scipy.stats.beta.cdf(rtpLower/10**4,a,b)
print 'prob between upper and lower (rtp): ' + str(prob)

#%% plot the posterior density for rtp

rtp = np.linspace(.98, 1.02, 10**3)

# this uses change of variables rule
eps = rtp * trueEpsilon
y = scipy.stats.beta.pdf(eps,a,b) * (1./trueEpsilon)
plt.plot(rtp,y)
plt.xlabel('rtp')
plt.title('posterior density')

#%% plot the posterior density for epsilon

x = np.linspace(0,3 * trueEpsilon, 10**3)
y = scipy.stats.beta.pdf(x,a,b)
plt.plot(x,y)
plt.xlabel('epsilon')
plt.title('posterior density')
