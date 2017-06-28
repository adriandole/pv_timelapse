import numpy as np
from skimage.transform import rescale, resize

initial_res = (0,0,0)


def process_frame(frame, resolution):
    """
    Performs various operations on a frame.

    :param frame: The video frame to process
    :type frame: np.ndarray
    :param resolution: Percentage to scale the frame by
    :type resolution: int
    :return: The processed frame
    """
    if resolution is not 100:
        scale = resolution / 100
        frame = rescale(frame, scale, mode='constant')
    global initial_res
    if initial_res == (0,0,0):
        initial_res = frame.shape
    frame_res = frame.shape
    if frame_res != initial_res:
        frame = resize(frame, initial_res)
    frame = horizontal_pad(frame)
    return frame


def horizontal_pad(frame, width_scale=0.2):
    """
    Pads the image horizontally with black.

    :param frame: The frame to pad
    :type frame: np.ndarray
    :param width_scale: Amount to pad, as multiple of current width
    :type width_scale: float
    :return:
    """
    shape = frame.shape
    pad_width = int(shape[1] * width_scale)
    frame = np.pad(frame, ((0, 0),(pad_width,pad_width),(0, 0)), 'constant')
    return frame
