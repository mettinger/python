from manim import *
import numpy as np

class Kuramoto(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        
        sphere = Sphere(radius = .1)
        sphere.set_color(RED)
        
        tracker = ValueTracker(0)
        sphere.add_updater(lambda mobject: mobject.move_to(axes.c2p(0.,0., np.sin(tracker.get_value()))))
        
        self.set_camera_orientation(phi=75. * DEGREES,theta=-75*DEGREES)
        tracker.add_updater(lambda mobject, dt: mobject.increment_value(dt))
        
        
        self.add(axes, sphere, tracker)
        self.wait(5)
         
        