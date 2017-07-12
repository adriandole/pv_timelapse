import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pv_timelapse.indexing import Params


def plot_ghi(p: Params) -> np.ndarray:
    """
    Creates an image of the GHI plot

    :param p: paramater container
    :return: the plot as an image
    """
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.plot(p.ghi_data, linewidth=1.0)
    canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return np.invert(image)
