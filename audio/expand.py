import os
import re
import sys
import json
import librosa
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

wavs = []
paths = []
silence = AudioSegment.silent(duration=200)
data = []
data_new = {}

def read_audio(audio_path):
    return AudioSegment.from_file(audio_path)

def split_on_silence_with_pydub(
        audio_path, skip_idx=0, out_ext="wav",
        silence_thresh=-40, min_silence_len=400,
        silence_chunk_len=100, keep_silence=100):

    audio = read_audio(audio_path)
#    print(len(audio))
    wavs.append(audio)
    paths.append(audio_path)
    return []

def combine_wavs_batch(audio_paths, method, **kargv):
    audio_paths.sort()
    method = method.lower()

    if method == "librosa":
        fn = partial(split_on_silence_with_librosa, **kargv)
    elif method == "pydub":
        fn = partial(split_on_silence_with_pydub, **kargv)

    parallel_run(fn, audio_paths,
            desc="Split on silence", parallel=False)

    audio_path = audio_paths[0]
    spl = os.path.basename(audio_path).split('.', 1)
    prefix = os.path.dirname(audio_path)+"/"+spl[0]+"."
    in_ext = audio_path.rsplit(".")[1]

    for i in range(len(wavs)-1):
        if len(wavs[i]) > 15000:
             continue
        if not paths[i] in data:
             continue

        sum = len(wavs[i])
        filename = prefix + str(i).zfill(4)+"."
        asr = data[paths[i]]+" "
        concated = wavs[i]
        for j in range(i+1, len(wavs)):
             sum += len(wavs[j])
             #sum += 200
             if sum > 15000:
                break
             if not paths[j] in data:
                break
             filename = filename + str(j).zfill(4) + "."
             asr = asr + data[paths[j]] + " "
             concated = concated + wavs[j]
             #if sum < 2000:
             #   continue
             final_fn = filename+"wav"
             data[final_fn] = asr
             concated.export(final_fn, format="wav")
             print(filename+"wav | "+str(len(concated)))

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_pattern', required=True)
    parser.add_argument('--alignment_path', required=True)
    parser.add_argument('--out_ext', default='wav')
    parser.add_argument('--method', choices=['librosa', 'pydub'], required=True)
    config = parser.parse_args()

    data = load_json(config.alignment_path, encoding="utf8")

    audio_paths = glob(config.audio_pattern)

    for path in audio_paths:
        single_path = path.replace('wav', '*.wav')
        single_paths = glob(single_path)
        combine_wavs_batch(
            single_paths, config.method,
            out_ext=config.out_ext,
        )
        wavs = []
        paths = []


    if os.path.exists(config.alignment_path):
        backup_file(config.alignment_path)

    write_json(config.alignment_path, data)
    get_durations(data.keys(), print_detail=False)
