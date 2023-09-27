
import csv

with open("/Users/iroro/Downloads/yovo/tts/Popóọlá_single_speaker_male/line_index_male.tsv", newline='') as tsvin:
# with open("/Users/iroro/Downloads/yovo/tts/Fọlákẹ́_single_speaker_female/line_index_female.tsv", newline='') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    text_dict = {}

    for row in tsvin:
        text = row[1]
        if text in text_dict:
            print("Duplicate found for {}, {} already exists".format(row[0], text_dict[text]))
        else:
            text_dict[text] = row[0]
