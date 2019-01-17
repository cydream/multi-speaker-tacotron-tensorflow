import json
import os.path
import argparse
from utils import backup_file, load_json, write_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--alignment_path', required=True)
    config = parser.parse_args()

    data_checked = {}
    data = load_json(config.alignment_path, encoding="utf8")

    for file in data:
        if os.path.exists(file):
            data_checked[file]=data[file]

    if os.path.exists(config.alignment_path):
        backup_file(config.alignment_path)

    write_json(config.alignment_path, data_checked)


