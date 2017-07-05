import warnings

import numpy as np
from skimage import img_as_ubyte
from skimage.transform import rescale, resize
from skimage.data import coffee
from skimage.viewer import ImageViewer

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
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return img_as_ubyte(frame)


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


def overlay(background, image, position=(0,1), buffer=5):
    """
    Overlays an image on top of another

    :param background: background image
    :type background: np.ndarray
    :param image: image to overlap
    :type image: np.ndarray
    :param position: where to overlay: (0,0) for bottom left
    :type position: tuple
    :param buffer: how many pixels away from the border to overlay
    :type buffer: int
    :return: the image with the overlay
    :rtype: np.ndarray
    """

    background = img_as_ubyte(background)
    image = img_as_ubyte(image)

    size = [n + buffer for n in image.shape]
    back_size = list(background.shape)
    if all([a > b for (a,b) in zip(size,back_size)]):
        raise ValueError('Overlay image too large')

    dim = image.shape
    if position == (0,0):
        background[buffer:dim[0]+buffer:, buffer:dim[1]+buffer:, ::] = image
    elif position == (0,1):
        background[-dim[0]-buffer:-buffer:, -dim[1]-buffer:-buffer:, ::] = image
    elif position == (1,1):
        background[buffer:dim[0]+buffer:, -dim[1]-buffer:-buffer:, ::] = image
    elif position == (1,0):
        background[buffer:dim[0]+buffer:, buffer:dim[1]+buffer:, ::] = image
    view = ImageViewer(background)
    view.show()
    return background

c = coffee()
o = rescale(c, 0.25)
overlay(c,o,(0,0))