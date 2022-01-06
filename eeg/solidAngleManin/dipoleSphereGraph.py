from manim import *

class dipoleSphereGraph(Scene):
    def construct(self):
        ax = Axes(x_range=[0, 4], 
                  y_range=[-2, 2], 
                  axis_config={"include_tip": False}, 
                  x_axis_config={"include_numbers":True})
        labels = ax.get_axis_labels(x_label="r", y_label="potential")
        
        t = ValueTracker(0)
        
        def func(x):
            if x < 1:
                return 1.0
            else:
                return -1/(x**2)
        
        graph = ax.plot(func, x_range=[0,4,.011], color=MAROON, use_smoothing=False)

        initial_point = [ax.coords_to_point(t.get_value(), func(t.get_value()))]
        dot = Dot(point=initial_point)

        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), func(t.get_value()))))
        
        self.add(ax, labels, graph, dot)
        
        self.play(t.animate(run_time=5, lag_ratio=0.0, rate_func=linear).set_value(4.0))
        self.wait()
        