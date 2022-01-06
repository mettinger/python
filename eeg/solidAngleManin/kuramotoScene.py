from manim import *
import numpy as np

class Kuramoto(ThreeDScene):
    def construct(self):
        
        '''
        numStep = 50
        x = np.linspace(0, 2 * np.pi, numStep)
        y = np.sin(x)
        index = 0
        '''
        
        rows, cols = 10,10
        numStep = 100
        
        odePhi = np.load('../odePhi.npy')
        nOsc, odeStep = odePhi.shape
        
        axes = ThreeDAxes()                                            
        #spheres = [Sphere(radius = .1, center=axes.c2p(row, col, odePhi[(row * cols) + col,0])) for row in range(rows) for col in range(cols)]
        
        spheres = [Sphere(radius = .1, center=np.array([row, col, odePhi[(row * cols) + col,0]])) for row in range(rows) for col in range(cols)]
        
        self.set_camera_orientation(phi=75. * DEGREES,theta=-75*DEGREES)
        self.add(axes, *spheres)
        self.move_camera(zoom=.5)
        
        '''
        for i in range(numStep):
            animations = [spheres[(row * cols) + col].animate.move_to(axes.c2p(row, col, odePhi[(row * cols) + col,i])) for row in range(rows) for col in range(cols)]
            self.play(*animations, run_time=.01)
        '''
        
        
         
        