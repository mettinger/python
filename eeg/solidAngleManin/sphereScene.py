from manim import *
import numpy as np

class SphereWithDipoles(ThreeDScene):
    
     def construct(self):
            axes = ThreeDAxes()
            sphere1 = Sphere()
            sphere1.set_opacity(.2)
            sphere2 = Sphere(radius=.05)
            sphere2.set_color(RED)
            
            self.set_camera_orientation(phi=75 * DEGREES,theta=-75*DEGREES)
            self.move_camera(zoom=2.0)
            
            self.add(axes)
            self.add(sphere1)
            self.play(sphere2.animate.shift(axes.c2p(4.0,0,0)), run_time=5, lag_ratio=0.0, rate_func=linear)
            
            
    