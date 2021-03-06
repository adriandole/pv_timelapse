import configparser
import os
import sys
from typing import Dict, Union


def configure(file: Union[
    os.path.abspath, str] = 'config.ini') -> configparser.ConfigParser:
    """Reads or creates a configuration file"""
    cfg = configparser.ConfigParser(interpolation=None)
    if not os.path.isfile(file):
        print('Creating new configuration file')
        cfg_file = open(file, 'w')
        cfg['Files'] = {
            'source directory':
                "M:\energy_netzero\photovoltaic_electrical\Images"
                                "\Sky Camera",
            'output directory': '', 'output name': '%Y-%m-%d.mp4',
            'overwrite': 'False', 'segmentation output name': '%Y-%m-%d.csv'}
        cfg['Formatting'] = {'image name format': '%Y-%m-%d--%H-%M-%S.jpg',
                             'folder name format': '%Y-%m-%d'}
        cfg['Video Options'] = {'frame rate': '60', 'duration': '10',
                                'resolution': '50'}
        cfg['Codec Options'] = {'windows preset': 'False',
                                'linear time': 'False',
                                'codec': 'h264', 'quality': '23',
                                'efficiency': '5',
                                'custom ffmpeg': '', 'threads': '4'}
        cfg['Timing'] = {'start day': '-1', 'end day': '-1', 'max days': '10'}
        cfg['Solar'] = {'latitude': '39.138306', 'longitude': '-77.219444',
                        'time zone': 'America/New_York', 'altitude': '140',
                        'minimum elevation': '-5'}
        cfg['Database'] = {'host': 'lumos.el.nist.gov', 'port': '3307',
                           'user': 'db_robot_select', 'password': 'vdv',
                           'database': 'vistavision_db',
                           'table name': 'ws_1_analogtable_0037',
                           'table column': '19_refcell1_wm2',
                           'time column': 'time_stamp'}
        cfg.write(cfg_file)
        cfg_file.write(
        ";                             Documentation\n"
        "; [Files]\n"
        "; source directory: Directory containing folders for each day's images.\n"
        ";                   Use UNC file paths (e.g. \\elwood\dir, not F:\dir)\n"
        "; output directory: Where to put the created timelapse.\n"
        "; output name: Name of the output file, extension will be removed.\n"
        ";              Supports datetime formatting.\n"
        "; overwrite: replace existing file if present\n"
        "; segmentation output name: name of CSV file for segmentation data."
        ";                           Blank to not compute."
        "; [Formatting]\n"
        "; image name format: Image name format containing date and time information.\n"
        ";                    Use Python's datetime formatting.\n"
        "; folder name format: Folder name format containing date (optionally time)\n"
        ";                     information. Use Python datetime formatting.\n\n"
        "; [Video Options]\n"
        "; frame rate: Frames per second of the output video.\n"
        "; duration: Length of the output video in seconds.\n"
        "; resolution: Scaling factor; percentage of source resolution.\n\n"
        "; [Codec Options]\n"
        "; windows preset: Preset for maximum compatibility with Windows Media Player.\n"
        ";                 Framerate, resolution, and codec options will be ignored.\n"
        "; linear time: Use constant time intervals between frames.\n"
        "; codec: Compression algorithm to use. Choices are h264 and h265.\n"
        "; quality: Amount of compression; higher = worse quality.\n"
        ";          0-51 allowed, 18-28 recommended.\n"
        "; efficiency: Compression efficiency. No effect on quality. Higher efficiency =\n"
        ";             longer encoding time. 0 to 8\n"
        "; threads: how many CPU threads to use in parallel.\n"
        "; custom ffmpeg: Dict of custom output parameters for FFMPEG. Not recommended.\n\n"
        "; [Timing]\n"
        "; start day: Which day to start making timelapses for. Either a date\n"
        ";            (YYYY-MM-DD) or a negative number. -1 = yesterday\n"
        "; end day: When to stop making timelapses, same options as start day.\n"
        "; max days: Maximum number of days to make timelapses for.\n\n"
        "; [Solar]\n"
        "; latitude: of the solar panel location in decimal degree form.\n"
        "; longitude: in decimal degree form.\n"
        "; altitude: above sea level in meters.\n"
        "; time zone: name from the tz database (e.g. America/New_York)\n"
        "; minimum elevation: Solar zenith angle to use as the start of the timelapse.\n\n"
        "; [Database]\n"
        "; host: SQL host containing a table with irradiance information.\n"
        "; port: corresponding to the host.\n"
        "; user: username for database access.\n"
        "; password: for the above username.\n"
        "; database: name of the database containing the relevant table.\n"
        "; table name: of the table to query from.\n"
        "; table column: name of the column to pull data from.\n"
        "; time column: name of the column containing datetime information.")
        cfg_file.close()
    cfg.read(file)
    try:
        if cfg.getint('Timing', 'start day') >= 0 or cfg.getint('Timing',
                                                                'end day') >= 0:
            sys.exit('Start and end day must be less than 0')
    except:
        pass
    if cfg['Codec Options']['codec'] not in ['h265', 'h264']:
        sys.exit('Invalid codec')
    if cfg.getint('Codec Options', 'quality') not in range(52):
        sys.exit('Invalid quality value. Must be 0 to 8.')
    if cfg.getint('Codec Options', 'efficiency') not in range(9):
        sys.exit('Invalid efficiency value. Must be 0 to 8.')
    if cfg.getint('Video Options', 'resolution') <= 0:
        sys.exit('Invalid resolution')
    if not os.path.isdir(cfg['Files']['source directory']):
        sys.exit('Source directory not found')
    return cfg


def create_dict(cfg: configparser.ConfigParser) -> Dict[str, dict]:
    """
    Creates FFMPEG input and output dictionaries

    :param cfg: loaded configuration file
    :return: input and output dictionaries
    """
    input_dict = {'-r': cfg['Video Options']['frame rate']}
    # if in_args.custom is not None:
    #     logging.info('Using custom FFMPEG parameters')
    #     output_dict = in_args.custom
    if cfg.getboolean('Codec Options', 'windows preset'):
        input_dict = {'-r': '30'}
        output_dict = {'-codec:v': 'mpeg4', '-flags:v': '+qscale',
                       '-global_quality:v': '0'}
    else:
        codecs = {'h264': 'libx264', 'h265': 'libx265'}
        efficiency = {0: 'ultrafast', 1: 'superfast', 2: 'veryfast',
                      3: 'faster',
                      4: 'fast', 5: 'medium', 6: 'slow', 7: 'slower',
                      8: 'veryslow'}

        output_dict = {'-codec:v': codecs[cfg['Codec Options']['codec']],
                       '-preset': efficiency[cfg.getint('Codec Options',
                                                        'efficiency')],
                       '-crf': cfg['Codec Options']['quality']}
    return {'out': output_dict, 'in': input_dict}

if __name__ == '__main__':
    configure()