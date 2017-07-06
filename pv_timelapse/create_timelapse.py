import numpy as np
import pandas as pd
import warnings
from skimage.io import imread
from skvideo.io import FFmpegWriter

from pv_timelapse.frame_tools import process_frame
from pv_timelapse.indexing import ProgressBar


def create_timelapse(p):
    """
    Creates a time-lapse.

    :param p: Params container class for the timelapse
    :type p: pv_timelapse
    """

    total_frames = p.duration * p.framerate
    frame_times = np.linspace(pd.Timestamp(p.start_date).value,
                              pd.Timestamp(p.end_date).value, total_frames)

    frame_times = pd.to_datetime(frame_times)
    # Framerate has to be a string. Something do with the underlying skvideo code
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        frame_writer = FFmpegWriter(p.write, inputdict={"-r": str(p.framerate)})

    f_count = 0
    pbar = ProgressBar()
    if p.linear_time or (len(frame_times) > len(p.image_times)):
        for frame in frame_times:
            closest_img = p.image_times.get_loc(frame, method='nearest')
            to_writer = process_frame(imread(p.date_to_path(p.image_times[closest_img])),
                                      p.resolution)
            frame_writer.writeFrame(to_writer)
            f_count += 1
            pbar.update(f_count / len(frame_times))
    else:
        skip = int(len(p.image_times)/len(frame_times))
        for n in range(0, len(p.image_times), skip):
            to_writer = process_frame(imread(p.date_to_path(p.image_times[n])),
                                      p.resolution)
            frame_writer.writeFrame(to_writer)
            pbar.update((n+1) / len(p.image_times))
    pbar.update(1)

    frame_writer.close()
