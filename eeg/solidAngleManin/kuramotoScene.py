from manim import *
import numpy as np
import pandas as pd

class Kuramoto(ThreeDScene):
    def construct(self):
        
        numAnimationStep = 100

        df = pd.read_csv("C:\\Users\\the_m\\github\\python\\eeg\\julia\\kuramoto_Out_01-18-16-28.csv")
        odePhi = df.values[:,1:].transpose()

        nOsc, timesteps = odePhi.shape
        rows = cols = int(np.sqrt(nOsc))
        # rows, cols = 10,10

        axes = ThreeDAxes()                                            
        #spheres = [Sphere(radius = .1, center=axes.c2p(row, col, odePhi[(row * cols) + col,0])) for row in range(rows) for col in range(cols)]
        
        spheres = [Sphere(radius = .1, center=np.array([row, col, odePhi[(row * cols) + col,0]])) for row in range(rows) for col in range(cols)]
        
        self.set_camera_orientation(phi=75. * DEGREES,theta=-75*DEGREES)
        self.move_camera(zoom=.5)
        self.add(axes, *spheres)

        animationSteps = np.linspace(0,timesteps - 1,numAnimationStep, dtype=np.int32)

        for i in animationSteps:
            animations = [spheres[(row * cols) + col].animate.move_to(axes.c2p(row, col, odePhi[(row * cols) + col,i])) for row in range(rows) for col in range(cols)]
            self.play(*animations, run_time=1.0)
        
        
        
         
        