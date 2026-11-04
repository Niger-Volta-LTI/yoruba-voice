import csv
import glob
import uuid
import os

# with open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_original.tsv', newline='') as tsvin, \
with open('/Users/iroro/Downloads/yovo/asr_20230910/All_20k_lines_ASR_completed_iofixed.tsv', newline='') as tsvin, \
    open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr.tsv', newline='') as tsv_old_idx_spkid, \
    open('/Users/iroro/Downloads/yovo/asr_20230910/line_index_asr.tsv', 'w', newline='') as tsvout:
    tsvin = csv.reader(tsvin, delimiter='\t')
    tsv_old_idx_spkid = csv.reader(tsv_old_idx_spkid, delimiter='\t')
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
    # Re-recorded sentences Speaker-ID calculus :[]
    folakemi_female_speaker_id = "20001-20237-FO505ae7"    # 256 (formerly 237) re-recorded sentences, female voice, new speaker-id. Start from 20001
    popoola_male_speaker_id =    "05251-05500-PB050cdf"    # 297 (formerly 282) re-recorded sentences, male voice, He already recorded 5251-5500, reuse speaker-id

    rerec_dir_female = "/Users/iroro/Downloads/yovo/asr_20230910/missing_files_single_speaker_female"
    rerec_dir_male = "/Users/iroro/Downloads/yovo/asr_20230910/missing_files_single_speaker_male"

    female_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_female + "/*.wav")]
    male_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_male + "/*.wav")]
    female_rerecording_count, male_rerecording_count, speaker_id_set = 0, 0, set()
    i = 0
    for row in tsvin:
        i += 1
        print(i, row)
        if i == 1698:
            break

    exit(0)
    # iterate over original Google doc TSV observing conditions and corner-cases
    for row in tsv_old_idx_spkid:
        wav_path = row[0]
        speaker_id = row[1]
        text = asr_completed_20k_text[count - 1][0].strip()

        if wav_path in female_file_list:
            speaker_id = folakemi_female_speaker_id
            female_rerecording_count += 1
        elif wav_path in male_file_list:
            speaker_id = popoola_male_speaker_id
            male_rerecording_count += 1

        # Track speaker-id count, we should have 81, original 80 (including Popoola) + Folakemi == 81
        speaker_id_set.add(speaker_id)
        print(count, speaker_id)

        # write out final TSV
        # tsvout.writerow([wav_path, speaker_id, text])
        count += 1

print("\n---------------------------------------------------------------------")
print("TSV sentence count: {}  speaker-id count: {}".format(count - 1 , len(speaker_id_set))) # count -1 for 1-based indexing
print("female_rerecording_count: {}  male_rerecording_count: {}".format(female_rerecording_count, male_rerecording_count))
print("---------------------------------------------------------------------")