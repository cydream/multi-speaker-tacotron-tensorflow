import os
import re
import sys
import json
import argparse
import numpy as np
from tqdm import tqdm
from glob import glob
from pydub import silence
from pydub import AudioSegment
from functools import partial

from hparams import hparams
from audio.get_duration import get_durations
from utils import load_json, write_json, parallel_run, add_postfix, backup_file
from audio import load_audio, save_audio, get_duration, get_silence


def read_audio(audio_path):
    return AudioSegment.from_file(audio_path)

def trim_on_silence(
        audio_path, skip_idx=0, out_ext="wav",
        silence_thresh=-40, min_silence_len=400,
        silence_chunk_len=100, keep_silence=200):

    audio = read_audio(audio_path)
    not_silence_ranges = silence.detect_nonsilent(
        audio, min_silence_len=silence_chunk_len,
        silence_thresh=silence_thresh)

    if not not_silence_ranges:
        print(audio_path)
        return[]

    start_idx = not_silence_ranges[0][0]
    end_idx = not_silence_ranges[-1][1]

    start_idx = max(0, start_idx - keep_silence)
    end_idx = min(len(audio), end_idx + keep_silence)

    trimmed = audio[start_idx:end_idx]
    trimmed.export(audio_path, out_ext)
    return []

def combine_wavs_batch(audio_paths, **kargv):
    audio_paths.sort()

    fn = partial(trim_on_silence, **kargv)

    parallel_run(fn, audio_paths,
            desc="Trimming on silence", parallel=False)

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_pattern', required=True)
    config = parser.parse_args()

    audio_paths = glob(config.audio_pattern)

    combine_wavs_batch(audio_paths)
