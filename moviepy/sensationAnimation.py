# %%
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from moviepy.video.io.bindings import mplfig_to_npimage
import moviepy.editor as mpy
from PIL import Image

# %%
#img = mpimg.imread('body2.png')
img = Image.open('body2.png')
newsize = (100,100)
img = img.resize(newsize)
plt.imshow(img)

# %%
rows,cols = img.size

imgArray = np.array(img)/255.

blueIndices = [[i,j] for i in range(rows) for j in range(cols) if imgArray[i,j,2] > .5]
blueCount = len(blueIndices)

# %%
duration = 10.0 

fig, ax = plt.subplots(1);
plt.sca(ax);
plt.axis('off');

def make_frame_mpl(t):
 
    thisArray = np.zeros((rows, cols, 3))
    thisPixel = blueIndices[np.random.randint(blueCount)] + [2]
    thisArray[*thisPixel] = 1.
    
    #thisArray = np.zeros((10,10,3))
    #thisArray[np.random.randint(0, 9), np.random.randint(0, 9),2] = 1.

    ax.imshow(thisArray);

    return mplfig_to_npimage(fig)

animation = mpy.VideoClip(make_frame_mpl, duration=duration);

# %%
#animation.ipython_display(fps=100, threads=32)

# %%
filename = 'sensation'
fps = 100

#animation.write_videofile(filename + '.mp4', fps=fps, threads=32)

animation.write_videofile(filename + '.mp4', 
                          fps=fps, threads=16, 
                          logger=None,codec="mpeg4",
                          preset="fast",
                          ffmpeg_params=['-b:v','10000k'], 
                          audio=False)
#animation.write_gif(filename + '.gif', fps=fps) 

# %%



