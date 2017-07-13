from typing import Union

import numpy as np
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pv_timelapse.indexing import Params


def plot_ghi(p: Params, img_date: datetime,
             data_freq: Union[int, float] = 1) -> np.ndarray:
    """
    Creates an image of the GHI plot

    :param p: paramater container
    :param img_date: date of the image being written
    :param data_freq: frequency in seconds of the input data
    :return: the plot as an image
    """
    date_delta = img_date - p.start_date
    data_date = date_delta.seconds / data_freq

    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.plot(p.ghi_data, linewidth=1.0)
    ax.axvline(data_date, color='r')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return np.invert(image)
