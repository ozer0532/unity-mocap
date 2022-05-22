import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")


def init_matplolib_figure():
    # plt.figure(num=0, figsize=(5, 4), dpi=100)
    # plt.clf()
    plt.figure(1)


def draw_3d_points(points):
    plt.axes(projection="3d")
    t = np.arange(0, 3, .01)
    plt.plot(t, 2 * np.sin(2 * np.pi * t))


def draw_figure(canvas):
    figure = plt.gcf()

    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


# https://stackoverflow.com/questions/63155989/automated-updating-matplotlib-plot-in-pysimplegui-window
class AnimatablePlot():
    def __init__(self, canvas) -> None:
        self.fig_agg = None
        self.figure = None
        self.canvas = canvas

    def init_fig(self, projection=None):
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111, projection=projection)

        self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas)
        self.fig_agg.draw()
        self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    def clear(self):
        self.axes.cla()
        self.axes.set_title("Triangulation Output")
        self.axes.set_xlabel("X axis")
        self.axes.set_ylabel("Y axis")
        self.axes.grid()

    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        self.axes.scatter(*args, **kwargs)

    def text(self, *args, **kwargs):
        self.axes.text(*args, **kwargs)

    def draw(self):
        # plt.show()
        self.fig_agg.draw()
