import os
import re
import sys
import json
import argparse
from functools import partial
from shutil import copyfile
from audio.get_duration import get_durations
from utils import load_json, write_json, parallel_run, add_postfix, backup_file

data = {}
new_data = {}
audio_path = ""

def copy_files(src_path):
    filename = os.path.basename(src_path)
    newfile = audio_path+filename
    #print(src_path + " ==> " + newfile + " : " + data[src_path])
    copyfile(src_path, newfile)
    new_data[newfile] = data[src_path]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--alignment_path', required=True)
    parser.add_argument('--target_dir', required=True)
    config = parser.parse_args()

    data = load_json(config.alignment_path, encoding="utf8")
    target_path = config.target_dir
    audio_path = target_path+"audio/"
    align_path = target_path+"alignment.json"

    if not os.path.exists(target_path):
        os.makedirs(target_path)
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    fn = partial(copy_files)
    parallel_run(fn, data.keys(), desc="Gather files", parallel=False)

    print(target_path)
    print(audio_path)

    if os.path.exists(align_path):
        backup_file(align_path)

    write_json(align_path, new_data)
    get_durations(data.keys(), print_detail=False)
#    write_json(config.alignment_path, data)
#    get_durations(data.keys(), print_detail=False)
