"""Shared text utilities for the ÌròyìnSpeech text-corpus analyses."""
import re
import unicodedata as ud

TONE_MARKS = {"̀", "́", "̄", "̂", "̌"}  # grave, acute, macron, circumflex, caron

_WORD = re.compile(r"(?:[^\W\d_][̀-ͯ]*)+")


def normalise(text):
    """Lower-case, map U+0329 (vertical line below) to U+0323 (dot below),
    collapse doubled dots, and return NFC."""
    s = ud.normalize("NFD", text.lower()).replace("̩", "̣")
    s = re.sub("̣+", "̣", s)
    return ud.normalize("NFC", s)


def words(text):
    """Split text into words (letters plus their combining marks), NFC."""
    s = ud.normalize("NFD", normalise(text))
    return [ud.normalize("NFC", w) for w in _WORD.findall(s)]


def bare(word):
    """Remove every diacritic (tone marks and sub-dots)."""
    return "".join(c for c in ud.normalize("NFD", word) if not ud.combining(c))


def without_tones(word):
    """Remove tone marks but keep sub-dots."""
    return ud.normalize("NFC", "".join(c for c in ud.normalize("NFD", word) if c not in TONE_MARKS))


def tones_only(word):
    """Remove sub-dots but keep tone marks (for comparing tone marking alone)."""
    return "".join(c for c in ud.normalize("NFD", word) if c in TONE_MARKS or not ud.combining(c))
