# ÌròyìnSpeech Text Corpus: analysis scripts

These scripts reproduce the analyses reported in the data descriptor *The ÌròyìnSpeech Text Corpus: 24,905 Curated Yorùbá Sentences for Speech and Language Technology* (Journal of Open Humanities Data, revised version):

| Script | Paper | What it computes |
|---|---|---|
| `coverage.py` | Section 2.1 | Letter, vowel–tone, CV-syllable and syllabic-nasal coverage |
| `source_comparison.py` | Section 2.3, Table 1 | Tone-mark and sub-dot differences between sourced sentences and their upstream originals, by source |
| `adr_baseline.py` | Section 4, Table 2 | A bigram diacritic-restoration baseline trained on ÌròyìnSpeech and on MENYO-20k, tested on both |
| `yoruba_text.py` | (shared) | Normalisation, word splitting and diacritic-stripping helpers |

The scripts were written and run with the assistance of Claude (Anthropic), an AI assistant, under the first author's direction. The authors reviewed the methods and results.

## Requirements

Python 3.9 or later. Only the standard library is used; nothing needs installing.

## Data

1. **ÌròyìnSpeech Text Corpus**: download from Zenodo, https://doi.org/10.5281/zenodo.23138464, and unzip. The scripts use `iroyinspeech_text.txt` and `iroyinspeech_text_full.csv`.
2. **MENYO-20k**: `git clone https://github.com/uds-lsv/menyo-20k_MT` (results in the paper used commit `0f2b019c2264a90813559c2e1cd7143054a4c36c`).
3. **MasakhaNER 2.0** (needed for `source_comparison.py` only): `git clone https://github.com/masakhane-io/masakhane-ner` (commit `ba5843cd08aa491d5f96a5e809e71eb9ec461391`). The Yorùbá files are in `MasakhaNER2.0/data/yor/`.

## Running

```
python coverage.py iroyinspeech-text-corpus/iroyinspeech_text.txt

python source_comparison.py iroyinspeech-text-corpus/iroyinspeech_text_full.csv \
    menyo-20k_MT masakhane-ner/MasakhaNER2.0/data/yor

python adr_baseline.py iroyinspeech-text-corpus/iroyinspeech_text_full.csv menyo-20k_MT
```

`coverage.py` runs in seconds. The other two take a few minutes each. Results are deterministic (the random seed for the ÌròyìnSpeech test split is fixed at 13).

## Method notes

- **Normalisation.** All text is lower-cased and NFC-normalised. U+0329 COMBINING VERTICAL LINE BELOW is mapped to U+0323 COMBINING DOT BELOW, so that encoding variants are not counted as diacritic differences.
- **Coverage.** Unmarked vowels are counted as mid tone. Syllabic nasals are counted only where tone-marked.
- **Source comparison.** Each corpus sentence is aligned with its most similar upstream sentence, comparing undiacritised words (difflib ratio ≥ 0.6). Words that match without diacritics are then compared with diacritics: a word counts as a tone difference if its tone marks differ, and as a sub-dot difference if its sub-dots differ (a word can be both). Many Voice of Nigeria sentences appear both in MENYO-20k and in the Yorùbá MasakhaNER 2.0 data; these are credited to Voice of Nigeria, so "Asejere" means MasakhaNER 2.0 sentences not also found in MENYO-20k. Differences include corrections, rewording and likely curation errors; the comparison measures disagreement between the two versions, not which is correct, and is an estimate, not a log of 2022 edits.
- **ADR baseline.** Each undiacritised word is mapped to the diacritised forms seen for it in training. A sequence is chosen by Viterbi decoding over an interpolated bigram/unigram model (λ = 0.7; add-one unigram smoothing). Unseen words are left undiacritised. Accuracy is exact word match. The ÌròyìnSpeech test set is 2,500 sentences with provenance `original_likely` (written in-house). Any ÌròyìnSpeech training sentence similar (ratio ≥ 0.5) to a MENYO-20k test or dev sentence is removed. The size-matched set is a random subset of the ÌròyìnSpeech training data with the same token count as the MENYO-20k training set.

## Expected output

`source_comparison.py`:
```
Source              aligned  changed   words  identical   tone  sub-dot
Asejere                 294      118    2579      93.8%   5.8%     0.5%
Voice of Nigeria        768      248    8179      95.9%   3.0%     1.4%
Global Voices            50       13     616      97.6%   1.5%     1.1%
All                    1112      379   11374      95.5%   3.5%     1.2%
```

`adr_baseline.py`:
```
Training data                    Tokens   Test: ÌròyìnSpeech   Test: MENYO-20k
ÌròyìnSpeech (full)              239123                 86.9              84.5
ÌròyìnSpeech (size-matched)      201688                 86.5              84.2
MENYO-20k train                  201683                 78.1              84.7
Both                             440806                 87.2              87.0
```

## Licence

The scripts are released under the MIT licence. The data they read keep their own licences (ÌròyìnSpeech Text Corpus: CC BY-NC 4.0; see the MENYO-20k and MasakhaNER repositories for theirs).
