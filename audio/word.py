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

def read_audio(audio_path):
    return AudioSegment.from_file(audio_path)

data = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_path', required=True)
    parser.add_argument('--json_path', required=True)
    config = parser.parse_args()

    filename = os.path.basename(config.audio_path).split(".", 1)[0]
    dir = os.path.dirname(config.audio_path)
    index = 0

    audio = read_audio(config.audio_path)

    asr_result = load_json(config.json_path, encoding="utf8")
    results = asr_result["response"]["results"]
    for item in results:
      words = item["alternatives"][0]["words"]
      for word in words:
        startTime = int(float(word["startTime"][:-1])*1000)
        endTime = int(float(word["endTime"][:-1])*1000)
        w = word["word"]
        print(startTime,endTime)
        target = "{}/{}.{:04d}.{}".format(dir, filename, index, "wav")
        index += 1
        wav = audio[startTime:endTime]
        wav.export(target, "wav")
        data[target]=w

    write_json(config.json_path+".out", data)
