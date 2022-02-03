#%%
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns

import plotly.io as pio
pio.renderers.default = 'plotly_mimetype+notebook' 

#%%
def orderParameterGet(phiVector):
    return np.abs(sum(np.exp(phiVector * (0+1j))))


# %%
df = pd.read_csv("c:\\Users\\the_m\\github\\python\\eeg\\julia\\kuramoto_Out_01-31-11-14.csv")

# %%
time = df.values[:,0]
odePhi = df.values[:,1:]
thetaDot = np.diff(odePhi, axis=0) * 10

# %%
index = -1
colorLower = np.min(thetaDot)
colorUpper = np.max(thetaDot)

px.scatter(x = np.cos(odePhi[index,:]), 
           y = np.sin(odePhi[index,:]), 
           color=thetaDot[index,:],
           range_color=(colorLower, colorUpper))

# %%
orderParameter = [orderParameterGet(odePhi[i,:])for i in range(len(time))]
plt.plot(time, orderParameter)

# %%
temp = thetaDot[0,:]

# %%
index = -5
sns.kdeplot(thetaDot[index,:])
# %%
from matplotlib import animation

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(-2,2), ylim=(-2, 2))
line, = ax.plot([], [], '.')
title = ax.set_title('')

# animation function.  This is called sequentially
def animate(i):
    #x = np.linspace(0, 2, 1000)
    #y = np.sin(2 * np.pi * (x - 0.01 * i))

    x = np.cos(odePhi[i,:])
    y = np.sin(odePhi[i,:])
    line.set_data(x, y)
    title.set_text(str(i))
    return line, title

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, frames=1000, interval=20, blit=True)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])



# %%
