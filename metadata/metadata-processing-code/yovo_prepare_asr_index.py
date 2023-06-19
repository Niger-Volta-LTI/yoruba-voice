import csv
import glob
import uuid
import os

with open('/Volumes/RR/yovo_asr/line_index.tsv', newline='') as tsvin, \
    open('/Volumes/RR/yovo_asr/line_index_asr.tsv', 'w', newline='') as tsvout:
    tsvin = csv.reader(tsvin, delimiter='\t')
    tsvout = csv.writer(tsvout, delimiter='\t')

    # ----------------------------------------------------------------
    # 1) iterate over raw export of 20k from Google Docs
    # 2) read TSV rows and write new columns for wave-path (utt-id) & speaker-id
    # 3) => Normalize male & female re-recording folders, otherwise badly formated files will cause metadata WAHALA
    # 4) => Initialize new speaker-id Popoola speaker-id which we reuse for (5251-5500) and all male re-recording
    # 5) => Initiaize new speaker-id for, Folakemi, the female re-recording
    # 6) => create list & sets to store male+female re-recording indicies & speaker-id counts. We use this to checksum
    # 7) As we iterate over all files, observe above conditions and write new indexes to match
    # 8) Finally, if all goes well, then male+female rerecording files can be safely copied into the main dir of 20k,
    #    overwriting the older badly recorded files

    count = 1                                                   # 1-based indexing, to match the Google docs
    single_asr_speaker_dir_size = 250

    folakemi_female_speaker_id = "20001-20237-FO505ae7"    # 237 re-recorded sentences, female voice, new speaker-id. Start from 20001
    popoola_male_speaker_id =    "05251-05500-PB050cdf"    # 282 re-recorded sentences, male voice, He already recorded 5251-5500, reuse speaker-id

    rerec_dir_female = "missing_files_single_speaker_female"
    rerec_dir_male = "missing_files_single_speaker_male"

    female_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_female + "/*.wav")]
    male_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_male + "/*.wav")]
    female_rerecording_count, male_rerecording_count, speaker_id_set = 0, 0, set()

    # iterate over original Google doc TSV observing conditions and corner-cases
    for row in tsvin:
        wav_path = str(count).zfill(5) + ".wav"
        text = row[0]
        if count % single_asr_speaker_dir_size == 1:
            speaker_id = str(count).zfill(5) + "-" + str(count + single_asr_speaker_dir_size - 1).zfill(5) + "-" + str(uuid.uuid4())[:8]
        verified = 'VER' if count < 10001 else 'UNVER'

        # Condition: we reuse popoola's speaker-id, which we've pre-allocated
        if count >= 5251 and count <= 5500:
            speaker_id = popoola_male_speaker_id

        # Condition: save original speaker-id for this batch of 250, in case we need a different
        #            speaker id, IF the current wav_path is a re-recording. Not great, but works :[]
        original_speaker_id = speaker_id

        if wav_path in female_file_list:
            speaker_id = folakemi_female_speaker_id
            female_rerecording_count += 1
        elif wav_path in male_file_list:
            speaker_id = popoola_male_speaker_id
            male_rerecording_count += 1

        # Track speaker-id count, we should have 81, original 80 (including Popoola) + Folakemi == 81
        speaker_id_set.add(speaker_id)
        print(count, speaker_id, verified)

        # write out final TSV
        tsvout.writerow([wav_path, speaker_id, verified, text])
        count += 1
        speaker_id = original_speaker_id


print("\n---------------------------------------------------------------------")
print("TSV sentence count: {}  speaker-id count: {}".format(count - 1 , len(speaker_id_set))) # count -1 for 1-based indexing
print("female_rerecording_count: {}  male_rerecording_count: {}".format(female_rerecording_count, male_rerecording_count))
print("---------------------------------------------------------------------")

# ---------------------------------------------------------------------
# TSV sentence count: 20000  speaker-id count: 81
# female_rerecording_count: 237  male_rerecording_count: 282
# ---------------------------------------------------------------------
