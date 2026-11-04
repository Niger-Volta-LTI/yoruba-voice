"""Compare tone marks and sub-dots in sourced sentences with their upstream originals
(paper, Section 2.3 and Table 1).

Each corpus sentence is aligned with its closest sentence in MENYO-20k (Voice of Nigeria,
Global Voices) or MasakhaNER 2.0 (Asejere), ignoring diacritics. For aligned sentences,
words that match once diacritics are removed are compared with diacritics in place.
Encoding variants (U+0329 for U+0323) are normalised away before comparison.
Sentences present in both MENYO-20k (Voice of Nigeria) and MasakhaNER 2.0 are credited
to Voice of Nigeria.

Usage:
  python source_comparison.py CORPUS_FULL_CSV MENYO_DIR MASAKHANER_YOR_DIR [--threshold 0.6]
"""
import argparse
import collections
import csv
import difflib
import glob
import os

from yoruba_text import bare, tones_only, without_tones, words


def load_upstream(menyo_dir, ner_dir):
    sents = []

    def add(source, line):
        t = words(line)
        if len(t) >= 3:
            sents.append((source, t))

    for f in sorted(glob.glob(os.path.join(menyo_dir, "verified", "von_part*_yo.txt"))):
        for line in open(f, encoding="utf-8"):
            add("Voice of Nigeria", line)
    for line in open(os.path.join(menyo_dir, "verified", "global_voices_new_yo.txt"), encoding="utf-8"):
        add("Global Voices", line)
    gv_csv = os.path.join(menyo_dir, "verified", "global_voices.csv")
    if os.path.exists(gv_csv):
        reader = csv.reader(open(gv_csv, encoding="utf-8"))
        header = next(reader)
        yo_cols = [i for i, h in enumerate(header) if "yo" in h.lower()]
        for row in reader:
            if yo_cols and len(row) > yo_cols[-1]:
                add("Global Voices", row[yo_cols[-1]])
    for f in sorted(glob.glob(os.path.join(ner_dir, "*.txt"))):
        tokens = []
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                if tokens:
                    add("Asejere", " ".join(tokens))
                    tokens = []
            else:
                tokens.append(line.split()[0])
        if tokens:
            add("Asejere", " ".join(tokens))

    # Many Voice of Nigeria sentences also appear in the Yorùbá MasakhaNER 2.0 data.
    # Credit those to Voice of Nigeria (their original outlet); 'Asejere' therefore means
    # MasakhaNER 2.0 sentences that are not also in the MENYO-20k Voice of Nigeria files.
    von = {" ".join(bare(w) for w in t) for s, t in sents if s == "Voice of Nigeria"}
    sents = [(s, t) for s, t in sents
             if not (s == "Asejere" and " ".join(bare(w) for w in t) in von)]

    seen, unique = set(), []
    for s, t in sents:
        key = (s, " ".join(t))
        if key not in seen:
            seen.add(key)
            unique.append((s, t))
    return unique


def trigrams(b):
    return {tuple(b[i:i + 3]) for i in range(len(b) - 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_csv")
    ap.add_argument("menyo_dir")
    ap.add_argument("ner_dir")
    ap.add_argument("--threshold", type=float, default=0.6)
    a = ap.parse_args()

    upstream = load_upstream(a.menyo_dir, a.ner_dir)
    up_bare = [[bare(w) for w in t] for _, t in upstream]
    index = collections.defaultdict(set)
    for i, b in enumerate(up_bare):
        for g in trigrams(b):
            index[g].add(i)

    rows = list(csv.DictReader(open(a.corpus_csv, encoding="utf-8")))
    stats = collections.defaultdict(collections.Counter)
    for row in rows:
        if row.get("duplicate") == "yes":
            continue
        t = words(row["text"])
        if len(t) < 3:
            continue
        b = [bare(w) for w in t]
        cand = collections.Counter()
        for g in sorted(trigrams(b)):
            for i in sorted(index.get(g, ())):
                cand[i] += 1
        best, best_ratio = None, 0.0
        for i, _ in sorted(cand.items(), key=lambda kv: (-kv[1], kv[0]))[:15]:
            r = difflib.SequenceMatcher(None, b, up_bare[i], autojunk=False).ratio()
            if r > best_ratio:
                best, best_ratio = i, r
        if best is None or best_ratio < a.threshold:
            continue
        source, ut = upstream[best]
        c = stats[source]
        c["sentences"] += 1
        changed = False
        for x, y, n in difflib.SequenceMatcher(None, b, up_bare[best], autojunk=False).get_matching_blocks():
            for k in range(n):
                ours, theirs = t[x + k], ut[y + k]
                c["words"] += 1
                if ours == theirs:
                    c["identical"] += 1
                    continue
                changed = True
                if tones_only(ours) != tones_only(theirs):
                    c["tone"] += 1
                if without_tones(ours) != without_tones(theirs):
                    c["dot"] += 1
        if changed:
            c["changed"] += 1

    total = collections.Counter()
    for c in stats.values():
        total.update(c)
    stats["All"] = total
    print(f"{'Source':18s} {'aligned':>8s} {'changed':>8s} {'words':>7s} {'identical':>10s} {'tone':>6s} {'sub-dot':>8s}")
    for s in ["Asejere", "Voice of Nigeria", "Global Voices", "All"]:
        c = stats[s]
        w = max(c["words"], 1)
        print(f"{s:18s} {c['sentences']:8d} {c['changed']:8d} {c['words']:7d} "
              f"{100 * c['identical'] / w:9.1f}% {100 * c['tone'] / w:5.1f}% {100 * c['dot'] / w:7.1f}%")


if __name__ == "__main__":
    main()
