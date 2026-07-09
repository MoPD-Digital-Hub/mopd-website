import html
import re

_BR_RE = re.compile(r'<br\s*/?>', re.IGNORECASE)
_TAG_RE = re.compile(r'<[^>]+>')


def plain_translation_text(value):
    """Strip markup and normalize translation copy for admin editing."""
    if value is None:
        return ''
    text = html.unescape(str(value))
    text = _BR_RE.sub('\n', text)
    text = _TAG_RE.sub('', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()
