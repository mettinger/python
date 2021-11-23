from manim import *

class DiskWithDipoles(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        #sphere=Sphere(radius=1)
        #sphere.set_fill(RED, opacity=1.0)
        
        gmText = Text("1G1M", font_size=40)
        self.add_fixed_in_frame_mobjects(gmText)
        gmText.to_corner(UL)
        
        cone1 = Cone(height=5.)
        cone1.set_fill(BLUE, opacity=0.5)
        cone1.move_to([0,0,2.5])
        
        cone2 = Cone(height=2.5)
        cone2.set_fill(BLUE, opacity=0.5)
        cone2.move_to([0,0,2.5/2.])
        
        disk = Cylinder(radius=1, height=.1)
        disk.set_fill(RED, opacity=1.0)
        
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES, zoom=.5)
        self.begin_ambient_camera_rotation(rate=1.0)
        
        self.add(axes)
        self.add(disk)
        self.add(cone1)
        self.play(Transform(cone1,cone2), run_time=5)
        #self.wait()

        #self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
        