import re

JUNK_LINE_RE = re.compile(r'^[\*\=\-_\s\.·]+$')
META_INLINE_RE = re.compile(
    r'by\s+admin|'
    r'\d*\s*min(?:ute)?s?(?:\s*\d+)?\s*read|'
    r'\d+\s*words?|'
    r'\b\d+\s*min(?:ute)?s?\b',
    re.IGNORECASE,
)


def clean_meta_noise(text):
    text = (text or '').strip()
    text = META_INLINE_RE.sub('', text)
    text = re.sub(r'[\s\-–—|]+', ' ', text).strip(' -–—|')
    return text.strip()


def is_junk_paragraph(text):
    text = (text or '').strip()
    if not text:
        return True
    if JUNK_LINE_RE.match(text):
        return True
    cleaned = clean_meta_noise(text)
    if not cleaned or JUNK_LINE_RE.match(cleaned):
        return True
    if len(cleaned) < 20 and META_INLINE_RE.search(text):
        return True
    if len(text) < 80 and META_INLINE_RE.search(text) and len(cleaned) < max(20, len(text) // 3):
        return True
    return False


def filter_paragraphs(paragraphs):
    return [clean_meta_noise(p) for p in paragraphs if not is_junk_paragraph(p)]


def truncate_text(text, length=140):
    text = clean_meta_noise(text)
    if not text:
        return ''
    if len(text) <= length:
        return text
    cut = text[:length].rsplit(' ', 1)[0]
    return f'{cut}…' if cut else f'{text[:length]}…'


def card_excerpt(title, excerpt, paragraphs, length=140):
    for candidate in [excerpt, *paragraphs]:
        cleaned = clean_meta_noise(candidate)
        if cleaned and not is_junk_paragraph(cleaned) and len(cleaned) >= 20:
            return truncate_text(cleaned, length)
    return truncate_text(title, length)
