import argparse
import os
import sys
import logging
from datetime import datetime

from pv_timelapse.create_timelapse import create_timelapse
from pv_timelapse.indexing import Params

parser = argparse.ArgumentParser()
parser.add_argument('--source_directory', '-sd', type=str, dest='sd',
                    help='Directory containing folders for each day\'s images')
parser.add_argument('--output_directory', '-od',
                    help='Where to output the time-lapse video',
                    type=str, dest='od', default='')
parser.add_argument('--output_name', '-on', help='Name of the output video',
                    type=str,
                    default='timelapse', dest='on')
parser.add_argument('--framerate', '-fps',
                    help='Frames per second of the output video',
                    type=int, default=60, dest='fps')
parser.add_argument('--duration', '-d', help='Duration of the output video',
                    type=int,
                    default=10, dest='d')
parser.add_argument('-s', '--start_datetime', type=str, dest='s',
                    help='Time-lapse start date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-e', '--end_datetime', type=str, dest='e',
                    help='Time-lapse end date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-imn', '--image_name', default='%Y-%m-%d--%H-%M-%S.jpg',
                    type=str,
                    dest='imn', help='Image name format containing date'
                                     'and time information. Use Python'
                                     ' datetime formatting.')
parser.add_argument('-fdn', '--folder_name', default='%Y-%m-%d', type=str,
                    help='Folder name format containing date (optionally time)'
                         ' information. Use Python datetime formatting.',
                    dest='fdn')
parser.add_argument('-r', '--resolution', type=int, default=100, dest='r',
                    help='Scaling factor; percentage of source resolution')
parser.add_argument('-c', '--codec', default='h264', type=str, dest='c',
                    help='Video codec to encode with', choices=['h265', 'h264'])
parser.add_argument('-q', '--quality', default=23, type=int, dest='q',
                    choices=range(0, 52),
                    help='Amount of compression; higher = worse quality. '
                         '18-28 recommended.')
parser.add_argument('-ef', '--efficiency', default=8, type=int, dest='ef',
                    choices=range(0, 9),
                    help='Compression efficiency. No effect on quality. '
                         'Higher efficiency'
                         ' = longer encoding time.')
parser.add_argument('--custom_ffmpeg', type=dict, default=None, dest='custom',
                    help='Custom output parameters for FFMPEG. Not '
                         'recommended.')
parser.add_argument('-lt', '--linear_time', action='store_true', dest='lt',
                    help='Use constant time intervals between frames')
parser.add_argument('-w', '--windows', action='store_true', dest='w',
                    help='Preset for maximum compatibility with Windows Media '
                         'Player')
in_args = parser.parse_args()

try:
    start_datetime = datetime.strptime(in_args.s, '%Y-%m-%dT%H:%M:%S')
    end_datetime = datetime.strptime(in_args.e, '%Y-%m-%dT%H:%M:%S')
except:
    sys.exit('Incorrect date format. Correct format is: YYYY-MM-DDThh:mm:ss')

if start_datetime >= end_datetime:
    sys.exit('End date must be later than start date')

if in_args.r <= 0:
    sys.exit('Invalid resolution')

try:
    source_path = os.path.abspath(in_args.sd)
    output_path = os.path.abspath(in_args.od)
except:
    sys.exit('Invalid directory')

if in_args.fps > 30 and in_args.r > 80:
    logging.warning('High frame rate and full resolution can cause playback'
                    ' issues on some computers.')

name, _ = os.path.splitext(in_args.on)
input_dict = {'-r': str(in_args.fps)}
if in_args.custom is not None:
    logging.info('Using custom FFMPEG parameters')
    output_dict = in_args.custom
    name += '.mp4'
elif in_args.w:
    name += '.avi'
    input_dict = {'-r': '30'}
    output_dict = {'-codec:v': 'mpeg4', '-flags:v': '+qscale',
                   '-global_quality:v': '0'}
    logging.warning('Using Windows preset: quality, efficiency, and framerate'
                    ' parameters ignored')
else:
    name += '.mp4'
    codecs = {'h264': 'libx264', 'h265': 'libx265'}
    efficiency = {0: 'ultrafast', 1: 'superfast', 2: 'veryfast', 3: 'faster',
                  4: 'fast', 5: 'medium', 6: 'slow', 7: 'slower', 8: 'veryslow'}

    output_dict = {'-codec:v': codecs[in_args.c],
                   '-preset': efficiency[in_args.ef],
                   '-crf': str(in_args.q)}

write_path = os.path.join(in_args.od, name)
if os.path.isfile(write_path):
    sys.exit('File already exists')

if not os.path.isdir(source_path):
    sys.exit('Source directory not found')

try:
    p = Params(source_path, write_path, start_datetime, end_datetime, in_args.d,
               in_args.r, in_args.fdn, in_args.imn, in_args.lt, input_dict,
               output_dict)
    create_timelapse(p)
except Exception as e:
    print(e)

sys.exit()
