#!/usr/bin/python3

tts_lines_in_asr_corpus = []

# open and clean asr lines
with open('asr_20k.txt','r') as asr_file:
    asr_lines = asr_file.readlines()
    for i in range(len(asr_lines)):
        asr_lines[i] = asr_lines[i].strip()

# open and clean tts lines. Format is 1-3000 Popóọlá, 3001-6000: Fọlákẹ́
with open('tts_aggregate_6k.txt','r') as tts_file:
    tts_lines = tts_file.readlines()
    for i in range(len(tts_lines)):
        tts_lines[i] = tts_lines[i].strip()

# brute force check
tts_index = 1
for one_tts_line in tts_lines:
    for one_asr_line in asr_lines:
        if one_tts_line in one_asr_line:
            tts_lines_in_asr_corpus.append((tts_index, one_tts_line))
    tts_index += 1

print("the number of tts lines in the asr corpus is: {}".format(len(tts_lines_in_asr_corpus)))
print(tts_lines_in_asr_corpus)
