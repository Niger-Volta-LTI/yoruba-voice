import glob
import soundfile as sf
import resampy
import librosa
import os


resampled_audio_path = "/Users/iroro/Downloads/yovo/FINAL_TTS_Oct_2023/resampled_files/"
all_audio_path = "/Users/iroro/Downloads/yovo/FINAL_TTS_Oct_2023/Popóọlá_single_speaker_male"
all_audio_list = [x for x in glob.glob(all_audio_path + "/*.wav")]

# Iterate all 20k audio files and verify the sample rate is 48kHz, keep track of counts
good_sr_count, good_sr = 0, 48000
bad_sr_count = 0
for audio_file_path in all_audio_list:
    # Load in audio file at its native sampling rate
    x, sr_orig = librosa.load(audio_file_path, sr=None)
    if int(sr_orig) == good_sr:
        good_sr_count += 1
    else:
        bad_sr_count += 1

        # x is now a 1-d numpy array, with `sr_orig` audio samples per second
        y = resampy.resample(x, sr_orig, good_sr, filter='kaiser_best')

        # write out new file
        resampled_file_path = resampled_audio_path + os.path.basename(audio_file_path)
        print(resampled_file_path)
        sf.write(resampled_file_path, y, good_sr, subtype='PCM_16')

print("\n-----------------------------------------------------------------------------------------")
print("good_sr_count: {}  bad_sr_count {}".format(good_sr_count, bad_sr_count))
print("-------------------------------------------------------------------------------------------")
