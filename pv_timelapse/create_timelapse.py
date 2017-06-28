from datetime import datetime

import numpy as np
import pandas as pd
from skimage.io import imread
from skvideo.io import FFmpegWriter

import pv_timelapse.indexing as ix
from pv_timelapse.frame_tools import process_frame


def create_timelapse(source_path, write_path, start_date, end_date,
                     duration, framerate, resolution, folder_format,
                     image_name_format):
    """
    Creates a time-lapse.

    :param source_path: Source directory containing sky camera images
    :type source_path: abspath
    :param write_path: Output file
    :type write_path: abspath
    :param start_date: When to start the time lapse.
    :type start_date: datetime
    :param end_date: When to finish the time lapse.
    :type end_date: datetime
    :param duration: Length of the output video in seconds.
    :type duration: int
    :param framerate: Video framerate in frames per second.
    :type framerate: int
    :param resolution: Output resolution as percentage of source
    :type resolution: int
    :param folder_format: Format of folder names containing date information
    :type folder_format: str
    :param image_name_format: Format of image names containing date and time information
    :type image_name_format: str
    """

    day_folders = ix.find_folders(start_date, end_date, source_path, folder_format)

    total_frames = duration * framerate
    frame_times = np.linspace(pd.Timestamp(start_date).value,
                              pd.Timestamp(end_date).value, total_frames)

    frame_times = pd.to_datetime(frame_times)
    # Framerate has to be a string. Something do with the underlying skvideo code
    frame_writer = FFmpegWriter(write_path, inputdict={"-r": str(framerate)})

    image_times = []

    for day_folder in day_folders:
        image_times += ix.index_files(source_path, day_folder, image_name_format)

    for frame in frame_times:
        if frame >= image_times[1]:
            image_times.pop(0)
        to_writer = process_frame(imread(ix.img_date_to_path(
            source_path, image_times[0], folder_format, image_name_format)),
            resolution)
        frame_writer.writeFrame(to_writer)

    frame_writer.close()
