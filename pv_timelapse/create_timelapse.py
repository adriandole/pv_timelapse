import warnings

import numpy as np
import pandas as pd
from skimage.io import imread

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from skvideo.io import FFmpegWriter

from pv_timelapse.frame_tools import process_frame
from pv_timelapse.indexing import ProgressBar, Params
from pv_timelapse.plotting import plot_ghi


def create_timelapse(p: Params):
    """
    Creates a time-lapse.

    :param p: Params container class for the timelapse
    """

    total_frames = p.duration * int(p.input_dict['-r'])
    frame_times = np.linspace(pd.Timestamp(p.start_date).value,
                              pd.Timestamp(p.end_date).value, total_frames)

    frame_times = pd.to_datetime(frame_times)
    # Framerate has to be a string. Something do with the underlying skvideo
    # code
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        frame_writer = FFmpegWriter(p.write, inputdict=p.input_dict,
                                    outputdict=p.output_dict)

    f_count = 0
    pbar = ProgressBar()
    if p.linear_time or (len(frame_times) > len(p.image_times)):
        for frame in frame_times:
            closest_img = p.image_times.get_loc(frame, method='nearest')
            img_date = p.image_times[closest_img]
            plot = plot_ghi(p, img_date)
            to_writer = process_frame(
                imread(p.date_to_path(img_date)),
                p.resolution, plot)
            frame_writer.writeFrame(to_writer)
            f_count += 1
            pbar.update(f_count / len(frame_times))
    else:
        skip = int(len(p.image_times) / len(frame_times))
        for n in range(0, len(p.image_times), skip):
            img_date = p.image_times[n]
            plot = plot_ghi(p, img_date)
            to_writer = process_frame(imread(p.date_to_path(img_date)),
                                      p.resolution, plot)
            frame_writer.writeFrame(to_writer)
            pbar.update((n + 1) / len(p.image_times))
    pbar.update(1)

    frame_writer.close()
