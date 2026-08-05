"""Simple blocklist checks for news comments (profanity / hate speech)."""

from __future__ import annotations

import re
import unicodedata

# Keep terms lowercase. Matched as whole tokens after normalization.
_BLOCKED_TERMS = frozenset({
    # English — strong profanity / sexual abuse
    'fuck', 'fucker', 'fucking', 'motherfucker', 'shit', 'bullshit',
    'asshole', 'bastard', 'bitch', 'cunt', 'dick', 'dickhead', 'pussy',
    'whore', 'slut', 'retard', 'retarded',
    # English — hate / slurs (non-exhaustive; extend as needed)
    'nigger', 'nigga', 'faggot', 'fag', 'kike', 'spic', 'chink', 'tranny',
    'rape', 'rapist', 'pedophile', 'paedophile',
    # Amharic / Ethiopic insults & hate (common forms)
    'ውሻ', 'አህያ', 'ጅል', 'ደደብ', 'ቆሻሻ', 'ዘረኛ', 'ጭራሮ',
})

_LEET = str.maketrans({
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '7': 't',
    '@': 'a',
    '$': 's',
})

# Split on whitespace; keep Ethiopic letters with word chars
_SPLIT = re.compile(r'\s+', re.UNICODE)
_STRIP_NOISE = re.compile(r'[^\w\u1200-\u137F]+', re.UNICODE)
_COLLAPSE = re.compile(r'(.)\1{2,}', re.UNICODE)


def _clean_token(token: str) -> str:
    token = unicodedata.normalize('NFKC', token or '')
    token = token.lower().translate(_LEET)
    token = _STRIP_NOISE.sub('', token)
    token = _COLLAPSE.sub(r'\1\1', token)
    return token


def find_blocked_language(text: str) -> str | None:
    """Return the first blocked term found in *text*, or None."""
    if not text or not text.strip():
        return None
    for raw in _SPLIT.split(unicodedata.normalize('NFKC', text).strip()):
        cleaned = _clean_token(raw)
        if cleaned in _BLOCKED_TERMS:
            return cleaned
    return None


def has_blocked_language(text: str) -> bool:
    return find_blocked_language(text) is not None
