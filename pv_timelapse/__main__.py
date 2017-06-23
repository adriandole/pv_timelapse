import argparse
import os
import sys
from datetime import datetime

from pv_timelapse.create_timelapse import create_timelapse

parser = argparse.ArgumentParser()
parser.add_argument('-source_dir', type=str, dest='source_dir',
                    help='Directory containing folders for each day\'s images')
parser.add_argument('-output_dir', help='Where to output the time-lapse video',
                    type=str, dest='output_dir', default='')
parser.add_argument('-output_name', help='Name of the output video', type=str,
                    default='timelapse', dest='output_name')
parser.add_argument('-fps', help='Frames per second of the output video',
                    type=int, default=60, dest='framerate')
parser.add_argument('-d', help='Duration of the output video', type=int,
                    default=10, dest='duration')
parser.add_argument('-start', type=str, dest='start_date',
                    help='Time-lapse start date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-end', type=str, dest='end_date',
                    help='Time-lapse end date. Format: YYYY-MM-DDThh:mm:ss')
parser.add_argument('-ffmpeg_path', dest='ffmpeg',
                    help='FFMPEG install directory containing ffmpeg.exe',
                    default=r"C:\ffmpeg-20170620-ae6f6d4-win64-static")
parser.add_argument('-image_name', default='%Y-%m-%d--%H-%M-%S.jpg', type=str,
                    dest='img_fmt', help='Image name format containing date'
                                         'and time information. Use Python'
                                         ' datetime formatting.')
parser.add_argument('-folder_name', default='%Y-%m-%d', type=str,
                    help='Folder name format containing date (optionally time)'
                         ' information. Use Python datetime formatting.',
                    dest='folder_fmt')
in_args = parser.parse_args()

try:
    start_datetime = datetime.strptime(in_args.start_date, '%Y-%m-%dT%H:%M:%S')
    end_datetime = datetime.strptime(in_args.end_date, '%Y-%m-%dT%H:%M:%S')
except:
    sys.exit('Incorrect date format. Correct format is: YYYY-MM-DDThh:mm:ss')

if start_datetime >= end_datetime:
    sys.exit('End date must be later than start date')

try:
    source_path = os.path.abspath(in_args.source_dir)
    output_path = os.path.abspath(in_args.output_dir)
except:
    sys.exit('Invalid directory')

name, _ = os.path.splitext(in_args.output_name)
name += '.mp4'
write_path = os.path.join(in_args.output_dir, name)
if os.path.isfile(write_path):
    sys.exit('File already exists')

if not os.path.isdir(source_path):
    sys.exit('Source directory not found')

try:
    create_timelapse(source_path, write_path, start_datetime,
                     end_datetime, in_args.duration, in_args.framerate,
                     in_args.folder_fmt, in_args.img_fmt)
except Exception as e:
    print(e)

sys.exit()
