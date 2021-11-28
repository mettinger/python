from manim import *

class DiskWithDipoles(ThreeDScene):
    
    outerDistance = 10.
    innerDistance = 5.
    discRadius = 1.0
    discHeight = .4
    zoom = .5
    
    #theta = np.arcsin((innerDistance/outerDistance) ** 2)
    theta = np.pi/3.
    vertex = np.array([0., innerDistance * np.cos(theta), innerDistance * np.sin(theta)])
    
    def truncatedCone(self, u, v):
        vector = np.array([DiskWithDipoles.discRadius * np.cos(u), DiskWithDipoles.discRadius * np.sin(u), DiskWithDipoles.discHeight/2.]) - DiskWithDipoles.vertex
        point = DiskWithDipoles.vertex + (vector * v)
        return np.array(point)
    
    def construct(self):
        axes = ThreeDAxes()
        
        disk = Cylinder(radius=DiskWithDipoles.discRadius, height=DiskWithDipoles.discHeight)
        disk.set_fill(RED, opacity=1.0)
        
        cone1 = Cone(height=DiskWithDipoles.outerDistance - (DiskWithDipoles.discHeight/2), base_radius=DiskWithDipoles.discRadius)
        cone1.set_fill(BLUE, opacity=0.5)
        cone1.move_to([0,0,DiskWithDipoles.outerDistance/2.])
        
        cone2 = Cone(height=DiskWithDipoles.innerDistance - (DiskWithDipoles.discHeight/2), base_radius=DiskWithDipoles.discRadius)
        cone2.set_fill(BLUE, opacity=1.0)
        cone2.move_to([0,0,DiskWithDipoles.innerDistance/2.])
        
        cone3 = cone1.copy()
        
        cone1Text = MathTex(r"\Omega_0 = \Omega(r_0)", font_size=40)
        cone1Text.shift(1.25* RIGHT + 3.0 * UP)
        
        cone2Text = MathTex(r"\Omega_1 = \Omega(\frac{r_0}{2}) = 4 \Omega_0", font_size=40)
        cone2Text.shift(2.0 * RIGHT + 3.0 * UP)
        
        cone3Text = MathTex(r"r = \frac{r_0}{2}, \theta = \frac{\pi}{3} \Rightarrow \Omega_2 \approx \frac{\Omega_1}{2}", font_size=40)
        cone3Text.next_to(cone3, UP + 2.0 * LEFT)
        
        dipoleText = Text("Dipole Layer").next_to(disk, RIGHT + UP)
        
        arrowText = MathTex(r"\pmb{\underset{-}{\overset{+}{\uparrow}}}", font_size=60, color=BLUE)
        arrowText.shift(2 * LEFT)
        
        surface = Surface(
            lambda u, v: axes.c2p(*self.truncatedCone(u, v)),
            u_range=[0, 2* PI],
            v_range=[0, 1.0]
        )
        
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES, zoom=DiskWithDipoles.zoom)
        
        self.play(Create(axes))
        self.play(Create(disk))
        self.wait(2)
        
        self.move_camera(zoom=1.2)
        self.add_fixed_in_frame_mobjects(arrowText)  
        self.play(Write(arrowText))
        self.add_fixed_in_frame_mobjects(dipoleText)  
        self.play(Write(dipoleText))
        self.wait(2)
        self.remove(dipoleText)
        self.remove(arrowText)
        self.move_camera(zoom=.3)
        
        
        self.play(Create(cone1))
        self.add_fixed_in_frame_mobjects(cone1Text)  
        self.play(Write(cone1Text))
        self.wait(2)
        self.remove(cone1Text)
        
        self.play(ReplacementTransform(cone1,cone2), run_time=2)
        self.move_camera(zoom=.75)
        self.add_fixed_in_frame_mobjects(cone2Text)  
        self.play(Write(cone2Text))
        self.wait(2)
        
        self.play(Create(surface))
        self.begin_ambient_camera_rotation(rate=1.0)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        self.add_fixed_in_frame_mobjects(cone3Text)  
        self.play(Write(cone3Text))
        self.wait(2)
        
        self.remove(cone2Text)
        self.move_camera(zoom=.3)
        self.play(ReplacementTransform(cone2,cone3), run_time=2)
        self.add(cone1Text)
        self.wait(3)
        
        
        

        