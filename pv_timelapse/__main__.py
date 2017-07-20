import os
import sys
from datetime import datetime, timedelta
from math import radians

import pytz
from pandas import Timestamp
from pvlib.solarposition import calc_time

from pv_timelapse.config import create_dict, configure
from pv_timelapse.create_timelapse import create_timelapse
from pv_timelapse.indexing import Params

cfg = configure()
dicts = create_dict(cfg)
max = cfg['Timing']['max days']

try:
    source_path = os.path.abspath(cfg['Files']['source directory'])
    output_path = os.path.abspath(cfg.get('Files', 'output directory',
                                          fallback=''))
except:
    sys.exit('Invalid directory')

basename, ext = os.path.splitext(cfg['Files']['output name'])

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
    endval = (end_day-first_day).days
except Exception as e:
    startval = cfg.getint('Timing', 'start day')
    endval = cfg.getint('Timing', 'end day')
    first_day = datetime.now(tz=tz)

if endval > cfg.getint('Timing','max days'):
    sys.exit('Too many days requested')

p = Params(source_path, cfg.getfloat('Video Options', 'duration'),
           cfg.getint('Video Options', 'resolution'),
           cfg['Formatting']['folder name format'],
           cfg['Formatting']['image name format'],
           cfg.getboolean('Codec Options', 'linear time'), dicts['in'],
           dicts['out'], cfg['Database']['user'], cfg['Database']['password'],
           cfg['Database']['host'], cfg.getint('Database', 'port'),
           cfg['Database']['database'], cfg['Database']['table name'],
           cfg['Database']['table column'], cfg['Database']['time column'])

for x in range(startval, endval + 1):
    start_day = Timestamp(first_day.year, first_day.month,
                          first_day.day).tz_localize(tz=tz) + timedelta(days=x)
    interval_noon = (start_day + timedelta(hours=12)).tz_convert('UTC')
    interval_end = (start_day + timedelta(hours=23, minutes=59)).tz_convert(
        'UTC')

    sunrise_utc = Timestamp(calc_time(start_day, interval_noon, latitude,
                                      longitude, 'alt', min, altitude=altitude),
                            tz='UTC')
    start_datetime = sunrise_utc.tz_convert(tz).tz_localize(
        None).to_pydatetime()
    sunset_utc = Timestamp(calc_time(interval_noon, interval_end, latitude,
                                      longitude, 'alt', min, altitude=altitude),
                            tz='UTC')
    end_datetime = sunset_utc.tz_convert(tz).tz_localize(None).to_pydatetime()

    try:
        name = datetime.strftime(start_datetime, basename)
    except:
        name = basename
        pass
    name = name + ext
    write_path = os.path.join(output_path, name)
    p.set_dates(start_datetime, end_datetime, write_path)
    create_timelapse(p)
