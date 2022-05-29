#!/usr/bin/env python3

# Grapheme-to-phoneme (G2P) conversion for Yorùbá using epitran & file of vocab words => X-SAMPA phonetic spellings

import argparse
import os.path
import unicodedata

import epitran
import marisa_trie
import panphon
import pkg_resources
import unicodecsv as csv

bad_tone_count = 0


class XSampaNVLTI(object):
    ipa2xs_fn = 'ipa-xsampa.csv'

    # IRORO COMMENT: Special phones are tonal or nasalisations that need to be "joined" to their base phone.
    # Since the symbols come in as NFD, if we blindly use delimiting, then these special phones will be separated
    # from their base, so we have special logic to apply them back to the base.
    #
    # The purpose of all this work is to create a nice space delimited lexicon.txt for Kaldi that supports
    # (1) ASCII (2) tones, diacritics etc (3) nasalizations (4) other factors
    # These are the reasons for the X-SAMPA choice, but conformed to the Kaldi toolkit, built around ARPABET
    special_phones = ['_L', '_H', '~']

    def __init__(self):
        """Construct an IPA-XSampa conversion object
        """
        self.trie = self._read_ipa2xs()
        self.ft = panphon.FeatureTable()

    def _read_ipa2xs(self):
        path = os.path.join('data', self.ipa2xs_fn)
        path = pkg_resources.resource_filename('epitran', path)
        pairs = []
        with open(path, 'rb') as f:
            reader = csv.reader(f, encoding='utf-8')
            next(reader)
            for ipa, xs, _ in reader:
                pairs.append((ipa, xs.encode('utf-8'),))
        trie = marisa_trie.BytesTrie(pairs)
        return trie

    def prefixes(self, s):
        return self.trie.prefixes(s)

    def longest_prefix(self, s):
        prefixes = self.prefixes(s)
        if not prefixes:
            return ''
        else:
            return sorted(prefixes, key=len)[-1]  # sort by length and return last

    def ipa2xs(self, ipa):
        """Convert IPA string (unicode) to X-SAMPA string
        Args:
            ipa (unicode): An IPA string as unicode
        Returns:
            list: a list of strings corresponding to X-SAMPA segments
            Non-IPA segments are skipped.
        """
        xsampa = []
        ipa = unicodedata.normalize('NFD', ipa)
        while ipa:
            token = self.longest_prefix(ipa)
            if token:
                xs = self.trie[token][0]  # take first member of the list
                xsampa.append(xs.decode('utf-8'))
                ipa = ipa[len(token):]
            else:
                ipa = ipa[1:]

        # Debug
        # if xsampa[0] in self.special_phones:
        #     print(xsampa)

        kaldi_xsampa_list = []
        i = len(xsampa) - 1

        # IRORO COMMENT: Iterate from last element of non-delimited tone sequences looking for special character. Go until
        # the 1st element, keep on decrementing i. If we reach the first element and it's a special tone, then raise
        # error. This has helped find a half-dozen badly marked characters with the tonal mark *before* the base char
        global bad_tone_count
        while i >= 0:
            curr_phone = xsampa[i]
            if curr_phone in self.special_phones:  # is an accent or nasalization, grab next phone & combine them
                try:
                    assert(i >= 1)
                except AssertionError:
                    # print(" ipa:  == {}".format(xsampa))
                    bad_tone_count += 1
                    break

                i -= 1
                next_phone = xsampa[i]
                combined = next_phone + curr_phone
                kaldi_xsampa_list.append(combined)
            else:
                kaldi_xsampa_list.append(curr_phone)

            i -= 1
        rev_kaldi_xsampa_list = [i for i in kaldi_xsampa_list[::-1]]

        return ' '.join(rev_kaldi_xsampa_list) # space delimited lexicon entries


def g2p_epitran(word_list):
    epi = epitran.Epitran('yor-Latn')  # Set to Yorùbá
    ipa_words = []

    for w in word_list:
        # gbogbo eniyan => IPA string: ɡ͡boɡ͡bo enijan
        ipa_word = epi.transliterate(w)
        ipa_words.append(ipa_word)

    return ipa_words


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""G2P""")
    parser.add_argument('vocab_file_path', type=str, help='a plaintext file with list of all words in the corpora, '
                                                          'for which we need phonetic spellings')
    args = parser.parse_args()

    word_list, xsampa_word_list = [], []
    with open(args.vocab_file_path, encoding='utf-8') as vocab_reader:
        for word in vocab_reader:
            word_list.append(word.strip())

    ipa_word_spellings = g2p_epitran(word_list)

    # X-Sampa class to convert IPA spellings to X-SAMPA with the delimiter of choice
    xs_nvlti = XSampaNVLTI()
    for ipa_word in ipa_word_spellings:
        s_a = xs_nvlti.ipa2xs(ipa_word)
        xsampa_word_list.append(s_a)

    # Debug
    # print("bad tone count: {}".format(bad_tone_count))

    # Debug: entire chain of transformations, does it look/sound legit?
    zipped = zip(word_list, ipa_word_spellings, xsampa_word_list)
    for z in zipped:
        print("{}       {}      {}".format(z[0], z[1], z[2]))


