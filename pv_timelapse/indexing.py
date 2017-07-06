import os
import pandas as pd
import MySQLdb
import sys
import time
import numpy as np
from datetime import datetime, timedelta


class Params:
    """Container class for various relevant parameters"""
    def __init__(self, source_path, write_path, start_date, end_date, duration,
                 framerate, resolution, folder_format, image_name_format, linear_time):
        """
        Constructor for the container class

        :param source_path: directory containing the day folders
        :type source_path: os.path.abspath
        :param write_path: path to the output video
        :type write_path: os.path.abspath
        :param start_date: when to start the timelapse
        :type start_date: datetime
        :param end_date: when to end the timelapse
        :type end_date: datetime
        :param duration: length of the video in seconds
        :type duration: int
        :param framerate: video framerate
        :type framerate: int
        :param resolution: output resolution as percentage of input
        :type resolution: int
        :param folder_format: name format of the day folders
        :type folder_format: str
        :param image_name_format: name format of the individual images
        :type image_name_format: str
        :param linear_time: whether to use constant time intervals between frames
        :type linear_time: bool
        """
        self.source = source_path
        self.write = write_path
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.framerate = framerate
        self.resolution = resolution
        self.folder_format = folder_format
        self.image_name_format = image_name_format
        self.linear_time = linear_time
        self.day_folders = self.find_folders()
        self.image_times = []
        for folder in self.day_folders:
            self.image_times += self.get_image_times(folder)
        self.image_times = pd.DatetimeIndex(self.image_times)
        self.ghi_data = self.get_ghi()

    def find_folders(self):
        """
        Finds the folders encompassing the given dates.

        :return: Name of the directory
        """

        dir_folders = os.listdir(self.source)
        days = []
        day_folders = []

        for folder_name in dir_folders:
            try:
                days += [datetime.strptime(folder_name, self.folder_format)]
            except:
                continue
        days.sort()
        start_day = self.start_date + \
                    timedelta(hours=-self.start_date.hour,
                              minutes=-self.start_date.minute, seconds=-self.start_date.second)

        for day in days:
            if (day >= start_day) and (day <= self.end_date):
                day_folders += [str(day)[0:10]]

        return day_folders

    def get_image_times(self, day_dir):
        """
        Returns a list of the dates of every picture in a folder.

        :param day_dir: Folder containing the image files
        :type day_dir: str
        :return: List of datetimes of the images
        """
        day_path = os.path.join(self.source, day_dir)

        file_dates = []
        for pic_name in os.listdir(day_path):
            try:
                file_dates += [datetime.strptime(pic_name, self.image_name_format)]
            except:
                continue
        file_dates.sort()

        return file_dates

    def date_to_path(self, img_date):
        """
        Finds the path of the image with the given date

        :param img_date: Date of the image
        :type img_date: datetime
        """
        folder_name = img_date.strftime(self.folder_format)
        image_name = img_date.strftime(self.image_name_format)
        return os.path.join(self.source, folder_name, image_name)

    def get_ghi(self):
        """
        Gets global horizontal irradiance values between the input dates

        :return: array of irradiance values every second
        :rtype: np.ndarray
        """
        db = MySQLdb.connect(host='lumos.el.nist.gov', port=3307, user='db_robot_select',
                             passwd='vdv', db='vistavision_db')
        c = db.cursor()
        c.execute('SELECT 19_refcell1_wm2 FROM ws_1_analogtable_0037 '
                  'WHERE time_stamp BETWEEN \'{}\' and \'{}\''
                  .format(self.start_date.strftime('%Y-%m-%d %H-%M-%S'),
                          self.end_date.strftime('%Y-%m-%d %H-%M-%S')))
        out = c.fetchall()
        return np.array([float(n[0]) for n in out])


class ProgressBar:

    def __init__(self, bar_length=20):
        """
        Creates a progress bar and records the inital time

        :param bar_length: length of the bar (default 20)
        :type bar_length: int
        """
        time.perf_counter()
        self.bar_length = bar_length
        self.start_time = time.time()

    def update(self, progress):
        """
        Updates and displays the progress bar
        
        :param progress: The progress to display
        :type progress: float
        """
        elapsed = time.time() - self.start_time
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
        if progress < 0:
            progress = 0
        if progress >= 1:
            progress = 1
        block = int(round(self.bar_length * progress))
        eta_seconds = (elapsed/progress) * (1-progress)
        eta = timedelta(seconds=eta_seconds)
        print("\rProgress: [{}] {:4.2f}% ETA: {:.7}".format("#" * block + "-" *
                              (self.bar_length - block), progress * 100, str(eta)),
              end='', flush=True)
