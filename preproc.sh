#! /bin/bash
normalize-audio ./datasets/$1/audio/*.wav
python3 -m audio.trim --audio_pattern="./datasets/$1/audio/*.wav"

cd datasets/$1
sed -i -e "s/fv01/$1/g" alignment.json

cd ../..
python3 checkfile.py --alignment_path="./datasets/$1/alignment.json"

cd datasets/$1/audio
for f in $1_t??_s02.wav; do touch ${f%_s02.wav}.wav; done;

cd ../../..

python3 -m audio.get_duration --data-path="./datasets/$1/alignment.json"

python3 -m audio.expand_ --audio_pattern="./datasets/$1/audio/$1_t??.wav" --method=pydub --alignment_path="./datasets/$1/alignment.json"

rm datasets/$1/audio/$1_t??.wav
