from datetime import datetime, timedelta
from typing import Union

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import LinearLocator, FuncFormatter

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
    data_date = (img_date-p.start_date).total_seconds() / data_freq

    def offset_formatter(x, pos=None):
        x_delta = timedelta(seconds=(x/data_freq))
        label_date = p.start_date + x_delta
        return label_date.strftime('%H:%M')

    locator = LinearLocator(numticks=8)
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    ax.plot(p.ghi_data, linewidth=1.0)
    ax.axvline(data_date, color='r')
    ax.text(0.35, 0.95,
            'Current: {:>7.1f} W/m²'.format(p.ghi_data[int(data_date)]),
            transform=ax.transAxes, ha='right', va='center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(FuncFormatter(offset_formatter))
    canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return np.invert(image)

