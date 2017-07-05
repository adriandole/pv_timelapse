import argparse
import os
import sys
import warnings
from datetime import datetime
from pv_timelapse.indexing import Params

from pv_timelapse.create_timelapse import create_timelapse

parser = argparse.ArgumentParser()
parser.add_argument('--source_directory', '-sd', type=str, dest='sd',
                    help='Directory containing folders for each day\'s images')
parser.add_argument('--output_directory', '-od', help='Where to output the time-lapse video',
                    type=str, dest='od', default='')
parser.add_argument('--output_name', '-on', help='Name of the output video', type=str,
                    default='timelapse', dest='on')
parser.add_argument('--framerate', '-fps', help='Frames per second of the output video',
                    type=int, default=60, dest='fps')
parser.add_argument('--duration', '-d', help='Duration of the output video', type=int,
                    default=10, dest='d')
parser.add_argument('-s', '--start_datetime', type=str, dest='s',
                    help='Time-lapse start date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-e', '--end_datetime', type=str, dest='e',
                    help='Time-lapse end date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-imn', '--image_name', default='%Y-%m-%d--%H-%M-%S.jpg', type=str,
                    dest='imn', help='Image name format containing date'
                                     'and time information. Use Python'
                                     ' datetime formatting.')
parser.add_argument('-fdn', '--folder_name', default='%Y-%m-%d', type=str,
                    help='Folder name format containing date (optionally time)'
                         ' information. Use Python datetime formatting.',
                    dest='fdn')
parser.add_argument('-r', '--resolution', type=int, default=100, dest='r',
                    help='Scaling factor; percentage of source resolution')
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
    warnings.warn('High frame rate and full resolution can cause playback'
                  ' issues on some computers.')

name, _ = os.path.splitext(in_args.on)
name += '.mp4'
write_path = os.path.join(in_args.od, name)
if os.path.isfile(write_path):
    sys.exit('File already exists')

if not os.path.isdir(source_path):
    sys.exit('Source directory not found')

try:
    p = Params(source_path, write_path, start_datetime, end_datetime, in_args.d,
               in_args.fps, in_args.r, in_args.fdn, in_args.imn)
    create_timelapse(p)
except Exception as e:
    print(e)

sys.exit()
