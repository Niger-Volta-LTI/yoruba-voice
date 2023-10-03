import csv
import glob
import os

# train
# with open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_final.tsv', newline='') as final, \
#     open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_train.tsv', newline='') as tsv_split, \
#     open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_train_new.tsv', 'w', newline='') as new_split:
#

# test
# with open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_final.tsv', newline='') as final, \
#     open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_test.tsv', newline='') as tsv_split, \
#     open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_test_new.tsv', 'w', newline='') as new_split:

# dev
with open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_final.tsv', newline='') as final, \
    open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_dev.tsv', newline='') as tsv_split, \
    open('/Users/iroro/github/yoruba-voice/metadata/asr/line_index_asr_dev_new.tsv', 'w', newline='') as new_split:

    final = csv.reader(final, delimiter='\t')
    tsv_split = csv.reader(tsv_split, delimiter='\t')
    new_split = csv.writer(new_split, delimiter='\t')

    final_list = list(final)
    print("final_list len: {}".format(len(final_list)))
    tsv_split_list = list(tsv_split)
    print("tsv_split_list len: {}".format(len(tsv_split_list)))

    # create new dictionary with keys and old data
    new_split_dict = {}
    for row in tsv_split_list:
        new_split_dict[row[0]] = [row[1], row[3]]

    # iterate through final list (with new speaker-id and text data), checking any matches for THIS SPLIT
    # and writing out original utt-id/wavpath and new data
    for final_row in final_list:
        uttid = final_row[0]
        if uttid in new_split_dict:
            new_split.writerow([uttid, final_row[1], final_row[2]])
