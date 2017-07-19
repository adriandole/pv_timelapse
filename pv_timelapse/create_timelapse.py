import warnings
import argparse
import sys
import os
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from skimage.io import imread

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from skvideo.io import FFmpegWriter

from pv_timelapse.frame_tools import process_frame
from pv_timelapse.indexing import ProgressBar, Params
from pv_timelapse.plotting import plot_ghi
from pv_timelapse.config import configure, create_dict


def create_timelapse(p: Params):
    """
    Creates a time-lapse.

    :param p: Params container class for the timelapse
    """
    total_frames = p.duration * int(p.input_dict['-r'])
    frame_times = np.linspace(pd.Timestamp(p.start_date).value,
                              pd.Timestamp(p.end_date).value, total_frames)

    frame_times = pd.to_datetime(frame_times)
    # Framerate has to be a string. Something do with the underlying skvideo
    # code
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        frame_writer = FFmpegWriter(p.write, inputdict=p.input_dict,
                                    outputdict=p.output_dict)

    f_count = 0
    pbar = ProgressBar()
    if p.linear_time or (len(frame_times) > len(p.image_times)):
        for frame in frame_times:
            closest_img = p.image_times.get_loc(frame, method='nearest')
            img_date = p.image_times[closest_img]
            plot = plot_ghi(p, img_date)
            to_writer = process_frame(
                imread(p.date_to_path(img_date)),
                p.resolution, plot)
            frame_writer.writeFrame(to_writer)
            f_count += 1
            pbar.update(f_count / len(frame_times))
    else:
        skip = int(len(p.image_times) / len(frame_times))
        for n in range(0, len(p.image_times), skip):
            img_date = p.image_times[n]
            plot = plot_ghi(p, img_date)
            to_writer = process_frame(imread(p.date_to_path(img_date)),
                                      p.resolution, plot)
            frame_writer.writeFrame(to_writer)
            pbar.update((n + 1) / len(p.image_times))
    pbar.update(1)

    frame_writer.close()

if __name__ == '__main__':
    """Running the timelapse creation script by itself"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_datetime', type=str, dest='s',
                        help='Time-lapse start date. Format: '
                             'YYYY-MM-DDThh:mm:ss')
    parser.add_argument('-e', '--end_datetime', type=str, dest='e',
                        help='Time-lapse end date. Format: YYYY-MM-DDThh:mm:ss')
    parser.add_argument('-cfg', '--config_file', type=str, dest='cfg',
                        help='Name or location of the config file to use',
                        default='config.ini')
    in_args = parser.parse_args()
    cfg = configure(in_args.cfg)

    try:
        start_datetime = datetime.strptime(in_args.s, '%Y-%m-%dT%H:%M:%S')
        end_datetime = datetime.strptime(in_args.e, '%Y-%m-%dT%H:%M:%S')
    except:
        sys.exit(
            'Incorrect date format. Correct format is: YYYY-MM-DDThh:mm:ss')

    if start_datetime >= end_datetime:
        sys.exit('End date must be later than start date')

    try:
        source_path = os.path.abspath(cfg['Files']['source directory'])
        output_path = os.path.abspath(cfg.get('Files', 'output directory',
                                              fallback=''))
    except:
        sys.exit('Invalid directory')

    name, _ = os.path.splitext(cfg['Files']['output name'])
    try:
        name = datetime.strftime(start_datetime, name)
    except:
        pass

    if cfg.getboolean('Codec Options', 'windows preset'):
        name += '.avi'
    else:
        name += '.mp4'
    write_path = os.path.join(output_path, name)

    if os.path.isfile(write_path) and cfg.getboolean('Files', 'overwrite'):
        logging.info('File already exists. Overwriting.')
    elif os.path.isfile(write_path) and not \
            cfg.getboolean('Files', 'overwrite'):
        sys.exit('Overwrite set to false and file already exists.')

    if not os.path.isdir(source_path):
        sys.exit('Source directory not found')

    dicts = create_dict(cfg)

    try:
        print('got here')
        p = Params(source_path, write_path, start_datetime, end_datetime,
                   cfg.getfloat('Video Options', 'duration'),
                   cfg.getint('Video Options', 'resolution'),
                   cfg['Formatting']['folder name format'],
                   cfg['Formatting']['image name format'],
                   cfg.getboolean('Codec Options', 'linear time'), dicts['in'],
                   dicts['out'])
        print('got here too')
        create_timelapse(p)
    except Exception as e:
        print(e)

    sys.exit()
