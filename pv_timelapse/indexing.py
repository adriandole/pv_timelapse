import os
import time
from datetime import datetime, timedelta
from typing import List, Iterator

import MySQLdb
import numpy as np
import pandas as pd


class Params:
    """Container class for various relevant parameters"""

    def __init__(self, source_path: os.path.abspath, duration: int,
                 resolution: int, folder_format: str, image_name_format: str,
                 linear_time: bool, input_dict: dict, output_dict: dict,
                 sql_user: str, sql_passwd: str, sql_host: str, sql_port: int,
                 sql_db: str, sql_table: str, table_column: str, time_col: str):
        """
        Constructor for the container class

        :param source_path: directory containing the day folders
        :param duration: length of the video in secondst
        :param resolution: output resolution as percentage of input
        :param folder_format: name format of the day folders
        :param image_name_format: name format of the individual images
        :param linear_time: whether to use constant time intervals between
        frames
        :param input_dict: FFmpeg input parameters
        :param output_dict: FFmpeg output parameters
        :param sql_user: username for accessing the irradiance database
        :param sql_passwd: password for the SQL user
        :param sql_host: host containing the database
        :param sql_port: port for the host
        :param sql_db: name of the database
        :param sql_table: name of the table to pull from
        :param table_value: which value to pull from the table
        :param time_col: column of the table containing datetime information
        """
        self.source = source_path
        self.write = None
        self.start_date = None
        self.end_date = None
        self.duration = duration
        self.resolution = resolution
        self.folder_format = folder_format
        self.image_name_format = image_name_format
        self.linear_time = linear_time
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.day_folders = None
        self.image_times = []
        self.ghi_data = None
        self.sql_user = sql_user
        self.sql_passwd = sql_passwd
        self.sql_host = sql_host
        self.sql_port = sql_port
        self.sql_db = sql_db
        self.sql_table = sql_table
        self.table_column = table_column
        self.time_col = time_col

    def set_dates(self, start_date: datetime, end_date: datetime,
                  write_path: os.path.abspath):
        """
        Sets the start and end dates and retrieves irradiance data

        :param start_date: when to start the timelapse
        :param end_date: when to end the timelapse
        :param write_path: path to the output video
        """
        self.start_date = start_date
        self.end_date = end_date
        self.write = write_path
        self.day_folders = self.find_folders()
        self.ghi_data = self.get_ghi()
        self.image_times = []
        for folder in self.day_folders:
            self.image_times += self.get_image_times(folder)
        self.image_times = pd.DatetimeIndex(self.image_times)

    def find_folders(self) -> Iterator[str]:
        """
        Finds the folders encompassing the given dates.

        :return: Name of the directory
        """
        dir_folders = os.listdir(self.source)
        days = []

        for folder_name in dir_folders:
            try:
                days += [datetime.strptime(folder_name, self.folder_format)]
            except:
                continue
        days.sort()
        start_day = datetime(self.start_date.year, self.start_date.month,
                             self.start_date.day)

        day_folders = map(lambda x: str(x)[0:10],
                          filter(lambda x: start_day <= x <= self.end_date,
                                 days))
        return day_folders

    def get_image_times(self, day_dir: str) -> List[datetime]:
        """
        Returns a list of the dates of every picture in a folder.

        :param day_dir: Folder containing the image files
        :return: List of datetimes of the images
        """
        day_path = os.path.join(self.source, day_dir)

        file_dates = []
        for pic_name in os.listdir(day_path):
            try:
                file_dates += [
                    datetime.strptime(pic_name, self.image_name_format)]
            except:
                continue
        file_dates.sort()

        return file_dates

    def date_to_path(self, img_date: datetime) -> os.path.abspath:
        """
        Finds the path of the image with the given date

        :param img_date: Date of the image
        """
        folder_name = img_date.strftime(self.folder_format)
        image_name = img_date.strftime(self.image_name_format)
        return os.path.join(self.source, folder_name, image_name)

    def get_ghi(self) -> np.ndarray:
        """
        Gets global horizontal irradiance values between the input dates

        :return: array of irradiance values every second
        """
        db = MySQLdb.connect(host=self.sql_host, port=self.sql_port,
                             user=self.sql_user, passwd=self.sql_passwd,
                             db=self.sql_db)
        c = db.cursor()
        c.execute('SELECT {} FROM {} '
                  'WHERE {} BETWEEN \'{}\' and \'{}\''
                  .format(self.table_column, self.sql_table, self.time_col,
                          self.start_date.strftime('%Y-%m-%d %H-%M-%S'),
                          self.end_date.strftime('%Y-%m-%d %H-%M-%S')))
        out = c.fetchall()
        return np.array([float(n[0]) for n in out])


class ProgressBar:
    def __init__(self, bar_length: int = 20):
        """
        Creates a progress bar and records the inital time

        :param bar_length: length of the bar (default 20)
        """
        time.perf_counter()
        self.bar_length = bar_length
        self.start_time = time.time()

    def update(self, progress: float):
        """
        Updates and displays the progress bar

        :param progress: The progress to display; [0,1]
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
        eta_seconds = (elapsed / progress) * (1 - progress)
        eta = timedelta(seconds=eta_seconds)
        print("\rProgress: [{}] {:4.2f}% ETA: {:.7}"
              .format("#" * block + "-" * (self.bar_length - block),
                      progress * 100, str(eta)), end='', flush=True)
