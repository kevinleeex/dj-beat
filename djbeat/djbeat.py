#!/usr/bin/env python3
# author: Kevin T. Lee<hello@lidengju.com>
# description: DJ-beat is available to detect the beat from the audio and generate time marks for FCPX and premiere.

__version__ = '0.4.9'

import madmom
import librosa
import argparse
import sys
import os
import datetime
import numpy as np
import re
from tqdm import tqdm
from pyfiglet import Figlet
from string import Template
from urllib.request import pathname2url


class DJbeat(object):

    # supported format list
    ext_list = ['mp3', 'wav']

    def __init__(self, filepath, fps=100, frame_rate=30, show_time=False):
        if not os.path.exists(filepath):
            raise Exception('The file {} not exists!'.format(filepath))

        self.filepath = filepath
        self.abs_filepath = os.path.abspath(self.filepath)
        self.src_dir = os.path.split(self.abs_filepath)[0]
        self.filename = os.path.split(self.abs_filepath)[-1]
        self.fileext = ''
        if '.' in self.filename:
            self.file_name = self.filename.split('.')[0]
            self.fileext = self.filename.split('.')[-1]
        if self.fileext not in DJbeat.ext_list:
            raise Exception(
                'Not supported file format, please use \'.mp3\', or \'.wav\'.')

        self.fps = fps
        self.frame_rate = frame_rate

        self.show_time = show_time

        self.build_version = __version__
        now = datetime.datetime.now()
        self.date_time = now.strftime('%Y-%m-%d %H:%M')

    def proc_data(self):
        print('[Start processing the audio...It may take a while]')
        # y: original audio, sr: sample rate
        self.y, self.audio_sr = librosa.load(self.filepath)
        self.file_time = (1.0 * len(self.y) / self.audio_sr)
        self.file_real_length = int(self.file_time * 1000)
        self.file_length = int(self.file_time) * 1000
        proc = madmom.features.beats.DBNBeatTrackingProcessor(look_ahead=0.4, fps=self.fps)
        act = madmom.features.beats.RNNBeatProcessor()(self.filepath)

        beat_times = proc(act)

        return beat_times

    def gen_fcpxml(self):
        beat_times = self.proc_data()
        markers = []
        real_time_list = []
        print('[Start write beat markers]')
        for item in tqdm(beat_times):
            real_time = item
            round_time = int(real_time*float(self.frame_rate))
            _mark = "<marker start='{round_time}/{frame_rate}s' duration='1/48000s' value='beat_at_{real_time}'  completed='0'/>".format(
                round_time=round_time, frame_rate=self.frame_rate, real_time=real_time)
            markers.append(_mark)
            real_time_list.append(str(real_time))

        self.beat_marks = '\n'.join(markers)
        
        new_file_name = re.sub(r'\W','_',self.file_name)
        _dict = {'build_version': self.build_version,
                 'date_time': self.date_time,
                 'frame_rate': self.frame_rate,
                 'file_name': new_file_name,
                 'file_path': pathname2url(self.abs_filepath),
                 'file_length': self.file_length,
                 'file_real_length': self.file_real_length,
                 'audio_sr': self.audio_sr,
                 'beat_marks': self.beat_marks}

        cur_dirpath = os.path.dirname(__file__)
        template_filepath = os.path.join(cur_dirpath, 'template.xml')
        with open(template_filepath, 'r') as f:
            src = Template(f.read())
            result = src.substitute(_dict)

        dst_filename = os.path.join(
            self.src_dir, '{}.fcpxml'.format(self.filename))

        with open(dst_filename, 'w') as out_f:
            out_f.write(result)
        if self.show_time:
            print('Beat time list (s): {}'.format(', '.join(real_time_list)))
        print('[Complete!]')


def main():
    # print logo
    f = Figlet(font='slant')
    print(f.renderText('DJ-Beat'))
    print('Author: Kevin T. Lee')
    print('Email: hello@lidengju.com')
    print('Github: https://github.com/kevinleeex/dj-beat')
    parser = argparse.ArgumentParser(
        description='DJ-beat, automatically mark the beat of your music for FCPX and PRE.')
    parser.add_argument('-f', '--filepath', default='', type=str,
                        help='The filepath of the input audio, support wav and mp3.')
    parser.add_argument('-r', '--frame_rate', default='30', choices=['23.98', '24', '25', '29.97', '30', '50', '60'],
                        help='The frame rate of your video setting.')
    parser.add_argument('-s', '--fps', default=100, type=int,
                        help='The sample rate of the music, a integer number.')
    parser.add_argument('-p', '--platform', default='fcpx', type=str, choices=['fcpx', 'pre'],
                        help='The platform, fcpx or pre')
    
    parser.add_argument('-V', help='to show the beat time list in terminal', action='store_true')
    parser.add_argument('-v', help='to show the version', action='store_true')

    args = vars(parser.parse_args())

    filepath = args['filepath']
    fps = args['fps']
    frame_rate = args['frame_rate']
    show_time = False

    if args['V']:
        show_time = True
    if args['v']:
        print('DJ-Beat Version: ', __version__)

    if filepath != '':
        _djbeat = DJbeat(filepath, fps, frame_rate, show_time)
        _djbeat.gen_fcpxml()
