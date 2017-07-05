import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def plot_ghi(p):
    """
    Creates an image of the GHI plot

    :param p: paramater container
    :type p: Params
    :return: the plot as an image
    :rtype: np.ndarray
    """
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.plot(p.ghi_data, linewidth=1.0)
    canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return image
