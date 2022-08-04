#%%
import numpy as np

#%%
def randomSample():
    a,b,c,d = np.random.random(4)
    ap = np.random.uniform(low=a)
    bp = np.random.uniform(low=b)
    cp = np.random.uniform(low=c)
    dp = np.random.uniform(low=d)

    G = ap*c + a*cp - ap*cp
    H = bp*d + b*dp - bp*dp
    K = ap*d + a*dp - ap*dp + bp*c + b*cp - bp*cp 

    return (K*K) - (4 * H * G), a,b,c,d,ap,bp,cp,dp


# %%

badList = []
numSamples = 100

for i in range(numSamples):
    result = randomSample()
    if result[0] < 0:
        badList.append(result)

print(len(badList))

# %%
