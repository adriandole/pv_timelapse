import os
import sys
from datetime import datetime, timedelta

from pv_timelapse.config import create_dict, configure
from pv_timelapse.create_timelapse import create_timelapse
from pv_timelapse.indexing import Params

cfg = configure()
dicts = create_dict(cfg)
now = datetime.now()
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
    start_day = datetime.strptime(cfg['Timing']['start day'], '%Y-%m-%d')
    end_day = datetime.strptime(cfg['Timing']['end day'], '%Y-%m-%d')
    startval = 0
    endval = (start_day-end_day).days
except:
    startval = cfg.getint('Timing', 'start day')
    endval = cfg.getint('Timing', 'end day')

if endval > cfg.getint('Timing','max days'):
    sys.exit('Too many days requested')

sub = 1
for x in range(startval, endval + 1):
    sunrise = timedelta(hours=0, minutes=0, seconds=0) # placeholder, will be calculated
    sunset = timedelta(hours=23, minutes=59, seconds=59)
    start_datetime = datetime(now.year, now.month, now.day)\
                     - timedelta(days=sub) + sunrise
    end_datetime = datetime(now.year, now.month, now.day)\
                     - timedelta(days=sub) + sunset

    try:
        name = datetime.strftime(start_datetime, basename)
    except:
        name = basename
        pass
    name = name + ext
    write_path = os.path.join(output_path, name)
    try:
        p = Params(source_path, write_path, start_datetime, end_datetime,
                   cfg.getfloat('Video Options', 'duration'),
                   cfg.getint('Video Options', 'resolution'),
                   cfg['Formatting']['folder name format'],
                   cfg['Formatting']['image name format'],
                   cfg.getboolean('Codec Options', 'linear time'), dicts['in'],
                   dicts['out'])
        create_timelapse(p)
    except Exception as e:
        print(e)
    sub += 1
