from manim import *

class Sigmoid(Scene):
    def construct(self):
        ax = Axes(x_range=[0, 2], y_range=[-100, 1, 10], axis_config={"include_tip": False})
        labels = ax.get_axis_labels(x_label="x", y_label="f(x)")

        t = ValueTracker(0)

        def func(x):
            return (100./(1. + np.exp(-10 * (x - 1)))) - 100
                    
        graph = ax.plot(func, color=MAROON)

        initial_point = [ax.coords_to_point(t.get_value(), func(t.get_value()))]
        dot = Dot(point=initial_point)

        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), func(t.get_value()))))
        
        #x_space = np.linspace(*ax.x_range[:2],200)
        #maximum_index = func(x_space).argmax()
        #self.play(t.animate(run_time=5, lag_ratio=0.0, rate_func=linear).set_value(x_space[maximum_index]))
        
        self.add(ax, labels, graph, dot)
        
        self.play(t.animate(run_time=5, lag_ratio=0.0, rate_func=linear).set_value(2.0))
        self.wait()
        