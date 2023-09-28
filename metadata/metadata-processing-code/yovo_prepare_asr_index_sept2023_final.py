import csv
import glob
import os

with open('/Users/iroro/Downloads/yovo/asr_20230910/All_20k_lines_ASR_completed.tsv', newline='') as tsvin, \
    open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr.tsv', newline='') as tsv_old_idx_spkid, \
    open('/Users/iroro/Downloads/yovo/asr_20230910/line_index_asr_final.tsv', 'w', newline='') as tsvout:

    tsvin = tsvin.read().splitlines()
    tsv_old_idx_spkid = csv.reader(tsv_old_idx_spkid, delimiter='\t')
    tsvout = csv.writer(tsvout, delimiter='\t')

    # ----------------------------------------------------------------
    # 1) iterate over raw export of 20k from Google Docs, as well as older/previous line-index
    # 2) DO NOT generate new speaker-ids, all that has changed are the re-recorded and the text files
    # 3) => In the case of re-recorded, we have a few more from {female,male} change the speaker-ids for these cases
    # 4) write old utt-id, speakerid (except for rerecorded) and new text from spreadsheet
    # 5) run in dry run mode first, to ensure we have 81 speakers, and all the numbers check out, bcos problem go dey

    count = 1                                                   # 1-based indexing, to match the Google docs
    # Re-recorded sentences Speaker-ID calculus :[]
    folakemi_female_speaker_id = "20001-20237-FO505ae7"    # 256 (formerly 237) re-recorded sentences, female voice, new speaker-id. Start from 20001
    popoola_male_speaker_id =    "05251-05500-PB050cdf"    # 297 (formerly 282) re-recorded sentences, male voice, He already recorded 5251-5500, reuse speaker-id

    rerec_dir_female = "/Users/iroro/Downloads/yovo/asr_20230910/missing_files_single_speaker_female"
    rerec_dir_male = "/Users/iroro/Downloads/yovo/asr_20230910/missing_files_single_speaker_male"

    female_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_female + "/*.wav")]
    male_file_list = [os.path.basename(x) for x in glob.glob(rerec_dir_male + "/*.wav")]
    female_rerecording_count, male_rerecording_count, speaker_id_set = 0, 0, set()

    # iterate over original Google doc TSV observing conditions and corner-cases
    for row in tsv_old_idx_spkid:
        wav_path = row[0]
        speaker_id = row[1]
        text = tsvin[count - 1]

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
        tsvout.writerow([wav_path, speaker_id, text])
        count += 1

print("\n---------------------------------------------------------------------")
print("TSV sentence count: {}  speaker-id count: {}".format(count - 1 , len(speaker_id_set))) # count -1 for 1-based indexing
print("female_rerecording_count: {}  male_rerecording_count: {}".format(female_rerecording_count, male_rerecording_count))
print("---------------------------------------------------------------------")