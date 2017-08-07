"""Boilerplate for later addition of a segmentation algorithm"""
import numpy as np
from typing import TextIO
from datetime import datetime
import csv


def compute_segmentation(image: np.ndarray, image_date: datetime,
                         csv_writer: csv.writer):
    """
    Writes segmentation data

    :param image: image to process
    :param image_date: date of the input image
    :param csv_file: file to write data to
    """
    csv_writer.writerow([str(image_date), algorithm(image)])


def algorithm(image: np.ndarray) -> float:
    """Implement segmentation algorithm here"""
    return 0