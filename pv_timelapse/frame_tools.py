import warnings

import numpy as np
from skimage import img_as_ubyte
from skimage.transform import rescale, resize

initial_res = (0, 0, 0)


def process_frame(frame: np.ndarray, resolution: int, plot) -> np.ndarray:
    """
    Performs various operations on a frame.

    :param frame: the video frame to process
    :param resolution: percentage to scale the frame by
    :return: the processed frame
    """
    if resolution is not 100:
        scale = resolution / 100
        frame = rescale(frame, scale, mode='constant')
    global initial_res
    if initial_res == (0, 0, 0):
        initial_res = frame.shape
    frame_res = frame.shape
    if frame_res != initial_res:
        frame = resize(frame, initial_res)
    frame = horizontal_pad(frame)
    # frame = overlay(frame, plot)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return img_as_ubyte(frame)


def horizontal_pad(frame: np.ndarray, width_scale: float = 0.2):
    """
    Pads the image horizontally with black.

    :param frame: the frame to pad
    :param width_scale: amount to pad, as multiple of current width
    :return: the padded frame
    """
    shape = frame.shape
    pad_width = int(shape[1] * width_scale)
    frame = np.pad(frame, ((0, 0), (pad_width, pad_width), (0, 0)), 'constant')
    return frame


def overlay(background: np.ndarray, image: np.ndarray,
            position: tuple = (0, 1), buffer: int = 5) -> np.ndarray:
    """
    Overlays an image on top of another

    :param background: background image
    :param image: image to overlap
    :param position: where to overlay: (0,0) for bottom left
    :param buffer: how many pixels away from the border to overlay
    :return: the image with the overlay
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        background = img_as_ubyte(background)
        image = img_as_ubyte(image)

    size = [n + buffer for n in image.shape]
    back_size = list(background.shape)
    if all([a > b for (a, b) in zip(size, back_size)]):
        raise ValueError('Overlay image too large')

    dim = image.shape
    if position == (0, 0):
        background[buffer:dim[0] + buffer:, buffer:dim[1] + buffer:, ::] = image
    elif position == (0, 1):
        background[-dim[0] - buffer:-buffer:, -dim[1] - buffer:-buffer:,
        ::] = image
    elif position == (1, 1):
        background[buffer:dim[0] + buffer:, -dim[1] - buffer:-buffer:,
        ::] = image
    elif position == (1, 0):
        background[buffer:dim[0] + buffer:, buffer:dim[1] + buffer:, ::] = image
    return background
