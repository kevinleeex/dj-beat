#!/usr/bin/env python3
# author: Kevin T. Lee<hello@lidengju.com>
# description: DJ-beat is available to detect the beat from the audio and generate time marks for FCPX and premiere.

import madmom
import librosa
import argparse
import sys
import os
import numpy as np
from string import Template


class djbeat(object):

    # supported format list
    ext_list = ['mp3', 'wav']

    def __init__(self, filepath, fps=100, frame_rate=30):
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
        if self.fileext not in djbeat.ext_list:
            raise Exception(
                'Not supported file format, please use \'.mp3\', or \'.wav\'.')

        self.fps = fps
        self.frame_rate = frame_rate

        self.build_version = '0.1'

    def proc_data(self):
        # y: original audio, sr: sample rate
        self.y, self.audio_sr = librosa.load(self.filepath)
        self.file_time = (1.0 * len(self.y) / self.audio_sr)
        self.file_real_length = int(self.file_time * 1000)
        self.file_length = int(self.file_time) * 1000
        proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=self.fps)
        act = madmom.features.beats.RNNBeatProcessor()(self.filepath)

        beat_times = proc(act)

        return beat_times

    def gen_fcpxml(self):
        beat_times = self.proc_data()
        markers = []
        for item in beat_times:
            real_time = item
            round_time = int(real_time*float(self.frame_rate))
            _mark = "<marker start='{round_time}/{frame_rate}s' duration='1/48000s' value='beat_at_{real_time}'  completed='0'/>".format(
                round_time=round_time, frame_rate=self.frame_rate, real_time=real_time)
            markers.append(_mark)

        self.beat_marks = '\n'.join(markers)


        _dict = {'build_version': self.build_version, 'frame_rate': self.frame_rate, 'file_name': self.file_name, 'file_path': self.abs_filepath,
                 'file_length': self.file_length, 'file_real_length': self.file_real_length, 'audio_sr': self.audio_sr, 'beat_marks': self.beat_marks}

        with open('./template.xml', 'r') as f:
            src = Template(f.read())
            result = src.substitute(_dict)

        dst_filename = os.path.join(self.src_dir,'{}.fcpxml'.format(self.filename))

        with open(dst_filename, 'w') as out_f:
            out_f.write(result)


def main():
    parser = argparse.ArgumentParser(
        description='DJ-beat, automatically mark the beat of your music for FCPX and PRE.')
    parser.add_argument('-f', '--filepath', type=str,
                        help='The filepath of the input audio', required=True)
    parser.add_argument('-s', '--fps', default=100, type=int,
                        help='The sample rate of the music, a integer number.', required=False)
    parser.add_argument('-r', '--frame_rate', default='30', choices=['23.98', '24', '25', '29.97', '30', '50', '60'],
                        help='The frame rate of your video setting.', required=True)

    args = vars(parser.parse_args())

    filepath = args['filepath']
    fps = args['fps']
    frame_rate = args['frame_rate']

    _djbeat = djbeat(filepath, fps, frame_rate)
    _djbeat.gen_fcpxml()


if __name__ == "__main__":
    main()