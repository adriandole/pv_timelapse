import numpy as np
import pandas as pd
from skimage.io import imread
from skvideo.io import FFmpegWriter

from pv_timelapse.frame_tools import process_frame


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
    frame_writer = FFmpegWriter(p.write, inputdict={"-r": str(p.framerate)})

    for frame in frame_times:
        closest_img = p.image_times.get_loc(frame, method='nearest')
        to_writer = process_frame(imread(p.date_to_path(p.image_times[closest_img])),
            p.resolution)
        frame_writer.writeFrame(to_writer)

    frame_writer.close()
