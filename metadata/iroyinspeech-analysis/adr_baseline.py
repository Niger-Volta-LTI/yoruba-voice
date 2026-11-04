"""Bigram diacritic-restoration (ADR) baseline: ÌròyìnSpeech vs MENYO-20k
(paper, Section 4 and Table 2).

The model maps each undiacritised word to the diacritised forms seen for it in training and
chooses a sequence with Viterbi decoding over an interpolated bigram/unigram word model.
Unseen words are left undiacritised. Accuracy is the share of words restored exactly.

Data handling:
  * ÌròyìnSpeech test set: 2,500 randomly chosen sentences with provenance
    'original_likely' (written in-house), seed 13.
  * ÌròyìnSpeech training set: all remaining unique sentences, minus any sentence whose
    undiacritised form is similar (ratio >= 0.5) to a MENYO-20k test or dev sentence.
  * Size-matched set: a random subset of the ÌròyìnSpeech training set with the same
    token count as the MENYO-20k training set.

Usage:
  python adr_baseline.py CORPUS_FULL_CSV MENYO_DIR
"""
import argparse
import collections
import csv
import difflib
import math
import os
import random

from yoruba_text import bare, words


def load_menyo(menyo_dir, split):
    out = []
    with open(os.path.join(menyo_dir, "data", f"{split}.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                t = words(parts[1])
                if t:
                    out.append(t)
    return out


class BigramRestorer:
    def __init__(self, corpus, lam=0.7):
        self.lam = lam
        self.cand = collections.defaultdict(collections.Counter)
        self.uni, self.bi = collections.Counter(), collections.Counter()
        for t in corpus:
            prev = "<s>"
            for w in t:
                self.cand[bare(w)][w] += 1
                self.uni[w] += 1
                self.bi[(prev, w)] += 1
                prev = w
            self.uni["<s>"] += 1
        self.n = sum(self.uni.values())
        self.v = len(self.uni) + 1

    def logp(self, prev, w):
        pu = (self.uni[w] + 1) / (self.n + self.v)
        pb = self.bi[(prev, w)] / self.uni[prev] if self.uni[prev] else 0.0
        return math.log(self.lam * pb + (1 - self.lam) * pu)

    def restore(self, bare_words):
        states = {"<s>": (0.0, [])}
        for b in bare_words:
            new = {}
            for w in (list(self.cand[b]) or [b]):
                score, path = max(((s + self.logp(p, w), pth) for p, (s, pth) in states.items()),
                                  key=lambda x: x[0])
                new[w] = (score, path + [w])
            states = new
        return max(states.values(), key=lambda x: x[0])[1]


def accuracy(model, test):
    ok = total = 0
    for t in test:
        for guess, gold in zip(model.restore([bare(w) for w in t]), t):
            total += 1
            ok += guess == gold
    return 100 * ok / total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_csv")
    ap.add_argument("menyo_dir")
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args()
    random.seed(a.seed)

    m_train, m_dev, m_test = (load_menyo(a.menyo_dir, s) for s in ("train", "dev", "test"))

    rows = [r for r in csv.DictReader(open(a.corpus_csv, encoding="utf-8")) if r["duplicate"] != "yes"]
    corpus = [(r["provenance_estimate"], words(r["text"])) for r in rows]
    corpus = [(p, t) for p, t in corpus if t]

    # index MENYO test+dev for overlap removal
    held = [[bare(w) for w in t] for t in m_test + m_dev]
    index = collections.defaultdict(set)

    def grams(b):
        return {tuple(b[i:i + 3]) for i in range(len(b) - 2)} or {tuple(b)}

    for i, b in enumerate(held):
        for g in grams(b):
            index[g].add(i)

    def near_menyo(t):
        b = [bare(w) for w in t]
        c = collections.Counter()
        for g in sorted(grams(b)):
            for i in sorted(index.get(g, ())):
                c[i] += 1
        return any(difflib.SequenceMatcher(None, b, held[i], autojunk=False).ratio() >= 0.5
                   for i, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:5])

    in_house = [t for p, t in corpus if p == "original_likely"]
    random.shuffle(in_house)
    i_test = in_house[:2500]
    test_keys = {" ".join(t) for t in i_test}
    i_train = [t for _, t in corpus if " ".join(t) not in test_keys]
    n_before = len(i_train)
    i_train = [t for t in i_train if not near_menyo(t)]

    def ntok(c):
        return sum(len(t) for t in c)

    shuffled = i_train[:]
    random.shuffle(shuffled)
    i_small, n = [], 0
    for t in shuffled:
        if n >= ntok(m_train):
            break
        i_small.append(t)
        n += len(t)

    print(f"ÌròyìnSpeech train: {len(i_train)} sentences, {ntok(i_train)} tokens "
          f"({n_before - len(i_train)} removed for overlap with MENYO-20k test/dev)")
    print(f"ÌròyìnSpeech test: {len(i_test)} sentences, {ntok(i_test)} tokens")
    print(f"MENYO-20k train: {ntok(m_train)} tokens; test: {len(m_test)} sentences, {ntok(m_test)} tokens\n")

    trains = [("ÌròyìnSpeech (full)", i_train), ("ÌròyìnSpeech (size-matched)", i_small),
              ("MENYO-20k train", m_train), ("Both", i_train + m_train)]
    print(f"{'Training data':30s} {'Tokens':>8s} {'Test: ÌròyìnSpeech':>20s} {'Test: MENYO-20k':>17s}")
    for name, data in trains:
        model = BigramRestorer(data)
        print(f"{name:30s} {ntok(data):8d} {accuracy(model, i_test):20.1f} {accuracy(model, m_test):17.1f}")


if __name__ == "__main__":
    main()
