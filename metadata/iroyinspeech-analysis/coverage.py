"""Grapheme, vowel-tone, CV-syllable and syllabic-nasal coverage (paper, Section 2.1).

Usage: python coverage.py path/to/iroyinspeech_text.txt
"""
import collections
import re
import sys
import unicodedata as ud

from yoruba_text import normalise

H, L, M = "́", "̀", "̄"
CONSONANTS = ["gb", "b", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r",
              "ṣ", "s", "t", "w", "y"]
VOWELS = ["a", "ẹ", "e", "i", "ọ", "o", "u"]
ALPHABET = ["a", "b", "d", "e", "ẹ", "f", "g", "gb", "h", "i", "j", "k", "l", "m", "n",
            "o", "ọ", "p", "r", "s", "ṣ", "t", "u", "w", "y"]
TONE = {H: "H", L: "L", M: "M", None: "M"}  # unmarked vowels carry mid tone

SYLLABLE = re.compile("(" + "|".join(CONSONANTS) + ")?(" + "|".join(VOWELS) + ")(̃)?([" + H + L + M + "])?"
                      "|([nm])([" + H + L + M + "])")


def show(g):
    return ud.normalize("NFC", g)


def main(path):
    lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
    text = ud.normalize("NFD", normalise(" ".join(lines)))
    word_list = re.findall(r"(?:[^\W\d_][̀-ͯ]*)+", text)

    cv, vowel_tone, nasal, letters = (collections.Counter() for _ in range(4))
    for w in word_list:
        base = ud.normalize("NFD", "".join(c for c in w if c == "̣" or not ud.combining(c)))
        for g in re.findall("gb|[a-z]̣?", base):
            letters[g] += 1
        i = 0
        while i < len(w):
            m = SYLLABLE.match(w, i)
            if not m:
                i += 1
                continue
            c, v, _, t, n, nt = m.groups()
            if v:
                vowel_tone[(v, TONE[t])] += 1
                cv[(c or "", v, TONE[t])] += 1
            else:
                nasal[(n, TONE[nt])] += 1
            i = m.end()

    print(f"Sentences: {len(lines)}")
    missing = [show(a) for a in ALPHABET if letters[a] == 0]
    print(f"Alphabet: {len(ALPHABET) - len(missing)} of {len(ALPHABET)} letters present; missing: {missing}")
    print("Rarest letters:", [(show(a), letters[a]) for a in sorted(ALPHABET, key=lambda a: letters[a])[:5]])

    vt = [(v, t) for v in VOWELS for t in "HML"]
    print(f"Vowel x tone: {sum(1 for x in vt if vowel_tone[x])} of {len(vt)} present; rarest:",
          [(show(v) + t, vowel_tone[(v, t)]) for v, t in sorted(vt, key=lambda x: vowel_tone[x])[:5]])

    toneless = [(c, v) for c in CONSONANTS for v in VOWELS]
    present = [x for x in toneless if any(cv[(x[0], x[1], t)] for t in "HML")]
    print(f"CV syllables (ignoring tone): {len(present)} of {len(toneless)} present")

    toned = [(c, v, t) for c in CONSONANTS for v in VOWELS for t in "HML"]
    absent = [show(c + v) + t for c, v, t in toned if cv[(c, v, t)] == 0]
    print(f"Tone-bearing CV syllables: {len(toned) - len(absent)} of {len(toned)} present; absent: {absent}")

    print("Tone-marked syllabic nasals:", {f"{n}{t}": k for (n, t), k in sorted(nasal.items())},
          "total", sum(nasal.values()))


if __name__ == "__main__":
    main(sys.argv[1])
