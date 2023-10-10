import csv
import glob
import uuid
import os

import soundfile as sf
import pyloudnorm as pyln





with open('/Users/iroro/github/yoruba-voice/tts_stats.tsv', 'w', newline='') as tsvout:
    tsvout = csv.writer(tsvout, delimiter='\t')

    count = 1
    audio_dir = "/Users/iroro/github/yoruba-voice/audio/tts"
    file_list = [x for x in glob.glob(audio_dir + "/*/*.wav")]

    meter = pyln.Meter(48000)  # create BS.1770 meter

    for audio_file_path in file_list:
        # print(audio_file_path)
        audio_samples, samplerate = sf.read(audio_file_path)  # load audio (with shape (samples, channels))
        loudness = meter.integrated_loudness(audio_samples)  # measure loudness
        duration = float(len(audio_samples)/samplerate)
        print(count, os.path.basename(audio_file_path), loudness, duration)

        # write out final TSV
        tsvout.writerow([os.path.basename(audio_file_path), loudness, duration])
        count += 1

print("\n------------------------------------")
print("TSV sentence count: {}".format(count))
print("--------------------------------------")
