import argparse
import logging
import os
import sys
from copy import copy
from datetime import datetime, timedelta
from math import radians
from multiprocessing import Pool

import pytz
from pandas import Timestamp
from pvlib.solarposition import calc_time

from pv_timelapse.config import create_dict, configure
from pv_timelapse.create_timelapse import create_timelapse
from pv_timelapse.indexing import Params

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', '--config_file', type=str, dest='cfg',
                        help='Name or location of the config file to use',
                        default='config.ini')
    in_args = parser.parse_args()

    cfg = configure(in_args.cfg)
    dicts = create_dict(cfg)
    max = cfg['Timing']['max days']

    try:
        source_path = os.path.abspath(cfg['Files']['source directory'])
        output_path = os.path.abspath(cfg.get('Files', 'output directory',
                                              fallback=''))
        seg_name = os.path.abspath(cfg.get('Files', 'segmentation output name',
                                              fallback=None))
    except:
        sys.exit('Invalid directory')

    basename, ext = os.path.splitext(cfg['Files']['output name'])
    seg_base = cfg['Files']['segmentation output name']

    if cfg.getboolean('Codec Options', 'windows preset'):
        ext = '.avi'
    else:
        ext = '.mp4'

    try:
        latitude = cfg.getfloat('Solar', 'latitude')
        longitude = cfg.getfloat('Solar', 'longitude')
        altitude = cfg.getfloat('Solar', 'altitude')
        min = radians(cfg.getfloat('Solar', 'minimum elevation'))
        tz = pytz.timezone(cfg['Solar']['time zone'])
    except Exception as e:
        print(e)
        sys.exit('Invalid solar parameters')

    try:
        first_day = Timestamp(cfg['Timing']['start day'], tz=tz)
        end_day = Timestamp(cfg['Timing']['end day'], tz=tz)
        startval = 0
        endval = (end_day - first_day).days
    except Exception as e:
        startval = cfg.getint('Timing', 'start day')
        endval = cfg.getint('Timing', 'end day')
        first_day = datetime.now(tz=tz)

    threads = cfg.getint('Codec Options', 'threads', fallback=1)

    if endval > cfg.getint('Timing', 'max days'):
        sys.exit('Too many days requested')

    base_param = Params(source_path, cfg.getfloat('Video Options', 'duration'),
                        cfg.getint('Video Options', 'resolution'),
                        cfg['Formatting']['folder name format'],
                        cfg['Formatting']['image name format'],
                        cfg.getboolean('Codec Options', 'linear time'),
                        dicts['in'], dicts['out'], cfg['Database']['user'],
                        cfg['Database']['password'], cfg['Database']['host'],
                        cfg.getint('Database', 'port'),
                        cfg['Database']['database'],
                        cfg['Database']['table name'],
                        cfg['Database']['table column'],
                        cfg['Database']['time column'], defer_img_indexing=True)

    param_container = []

    for x in range(startval, endval + 1):
        start_day = Timestamp(first_day.year, first_day.month,
                              first_day.day).tz_localize(tz=tz) + timedelta(
            days=x)

        folder_name = start_day.strftime(
            cfg['Formatting']['folder name format'])
        day_path = os.path.join(source_path, folder_name)
        if not os.path.isdir(day_path):
            logging.warning(f'Missing folder: {folder_name}')
            continue

        interval_noon = (start_day + timedelta(hours=12)).tz_convert('UTC')
        interval_end = (start_day + timedelta(hours=23, minutes=59)).tz_convert(
            'UTC')

        sunrise_utc = Timestamp(calc_time(start_day, interval_noon, latitude,
                                          longitude, 'alt', min,
                                          altitude=altitude),
                                tz='UTC')
        start_datetime = sunrise_utc.tz_convert(tz).tz_localize(
            None).to_pydatetime()
        sunset_utc = Timestamp(calc_time(interval_noon, interval_end, latitude,
                                         longitude, 'alt', min,
                                         altitude=altitude),
                               tz='UTC')
        end_datetime = sunset_utc.tz_convert(tz).tz_localize(
            None).to_pydatetime()

        try:
            name = datetime.strftime(start_datetime, basename)
        except:
            name = basename
        try:
            seg_name = datetime.strftime(start_datetime, seg_base)
        except:
            seg_name = seg_base
        name = name + ext
        write_path = os.path.join(output_path, name)
        if os.path.isfile(write_path) and cfg.getboolean('Files', 'overwrite'):
            logging.info('File already exists. Overwriting.')
        elif os.path.isfile(write_path) and not \
                cfg.getboolean('Files', 'overwrite'):
            logging.warning('Overwrite set to false and file already exists. '
                            'Skipping file.')
            continue
        logging.info(f'Pulling data and folder information for '
                     f'{start_datetime.strftime("%Y-%m-%d")}')
        p_add = copy(base_param)
        p_add.set_dates(start_datetime, end_datetime, write_path, seg_name)
        param_container += [p_add]

    with Pool(processes=threads) as pool:
        print(f'Simultaneous multithreading with {threads} threads')
        pool.map(create_timelapse, param_container)
