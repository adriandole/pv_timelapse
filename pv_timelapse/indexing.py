import os
from datetime import datetime


def find_folders(start_date, end_date, source_dir, folder_format):
    """
    Finds the folder encompassing the given start date.

    :param start_date: Datetime object representing the start date
    :type start_date: datetime
    :param end_date: Datetime object representing the end date
    :type end_date: datetime
    :param source_dir: The directory to look in
    :type source_dir: os.path.abspath
    :param folder_format: Format of the day folder names
    :type folder_format: str
    :return: Name of the directory
    """

    dir_folders = os.listdir(source_dir)
    days = []
    day_folders = []

    for folder_name in dir_folders:
        try:
            days += [datetime.strptime(folder_name, folder_format)]
        except:
            continue
    days.sort()
    start_date += timedelta(hours=-start_date.hour, minutes=-start_date.minute,
                            seconds=-start_date.second)

    for day in days:
        if (day >= start_date) and (day <= end_date):
            day_folders += [str(day)[0:10]]

    return day_folders


def index_files(source_path, day_dir, image_name_format):
    """
    Returns a list of the dates of every picture in a folder.

    :param source_path: Folder containing the day folders
    :type source_path: os.path.abspath
    :param day_dir: Folder containing the image files
    :type day_dir: str
    :param image_name_format: Format of the image names
    :type image_name_format: str
    :return: List of datetimes of the images
    """
    day_path = os.path.join(source_path, day_dir)

    file_dates = []
    for pic_name in os.listdir(day_path):
        try:
            file_dates += [datetime.strptime(pic_name, image_name_format)]
        except:
            continue
    file_dates.sort()

    return file_dates


def img_date_to_path(source_path, img_date, folder_format, image_name_format):
    """
    Finds the path of the image with the given date

    :param source_path: Folder containing the day folders
    :type source_path: os.path.abspath
    :param img_date: Date of the image
    :type img_date: datetime
    :param folder_format: Format of the day folder names
    :type folder_format: str
    :param image_name_format: Format of the image names
    :type image_name_format: str
    """
    folder_name = img_date.strftime(folder_format)
    image_name = img_date.strftime(image_name_format)
    return os.path.join(source_path, folder_name, image_name)
