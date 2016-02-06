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
trials = 10**9
#success = round(trials * trueEpsilon)
success = scipy.stats.binom.rvs(trials,trueEpsilon)
# use uniform beta prior
a = 1 + success
b = 1 + trials - success


rtpLower = .99
rtpUpper = 1.01
prob = scipy.stats.beta.cdf(rtpUpper/10**4,a,b) - scipy.stats.beta.cdf(rtpLower/10**4,a,b)
print 'prob between upper and lower (rtp): ' + str(prob)

#%%

alpha = .99
interval = np.array(scipy.stats.beta.interval(alpha, a, b, loc=0, scale=1)) * 10**4
print "interval length: " + str(interval[1] - interval[0])

#%% plot the posterior density for rtp

rtp = np.linspace(.99, 1.01, 10**3)

# this uses change of variables rule
eps = rtp * trueEpsilon
y = scipy.stats.beta.pdf(eps,a,b) * trueEpsilon
plt.plot(rtp,y)
plt.xlabel('rtp')
plt.title('posterior density for RTP with 1e9 samples \n .99 credible interval length = .016')
plt.savefig("/Users/mettinger/Google Drive/MyPapers/latex/boschPresentation/posteriorRTP.png")


#%% plot the posterior density for epsilon

delta = .000001
x = np.linspace(trueEpsilon - delta, trueEpsilon + delta, 10**3)
y = scipy.stats.beta.pdf(x,a,b)
plt.plot(x,y)
plt.xlabel('epsilon')
plt.title('posterior density for epsilon with 1e9 samples')
plt.savefig("/Users/mettinger/Google Drive/MyPapers/latex/boschPresentation/posteriorEpsilon.png")