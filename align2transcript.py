import json
import csv
from jamo import hangul_to_jamo
import argparse
from utils import load_json
from text.korean import normalize

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--alignment_path', required=True)
    parser.add_argument('--remove_prefix', required=True)
    config = parser.parse_args()

    data = load_json(config.alignment_path, encoding="utf8")
    out_txt = config.alignment_path.replace('alignment.json','transcript.txt')
    f = csv.writer(open(out_txt, "w"), delimiter='|')

    for file in data:
        filename = file.replace(config.remove_prefix, '')
        text = data[file]
        norm = normalize(text)
        decomp = list(hangul_to_jamo(norm))
        
        f.writerow([filename, text, norm, ''.join(decomp), "0.0"])



